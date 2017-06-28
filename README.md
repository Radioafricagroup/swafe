# Swafe
  Swafe is a python library for orchestrating AWS SWF workflows, simple as that.
  You can manage domains, workflows and activities via a cli and run deciders
  and workers as background processes


## Installation
  Swafe is available as a pip package. Currently in Alpha.
  ```
    $ pip install swafe
  ```

### After install

Ensure that you have specified the region you want to work on.

You can do this in one of two ways:

  1. You can specify you region in your ~/.aws/config file
    ```
      [default]
      region=us-west-2
    ```
  2. You can use the following environment variable
      ```
      export AWS_DEFAULT_REGION=us-west-2
      ```

## Getting started
  If you're not familiar with AWS SWF, you can get familiar [here](https://aws.amazon.com/swf/).

  We'll be creating a simple image processing workflow to demonstrate how to get started with swafe. This demo is based on the AWS SWF demo.

  ![Alt](/examples/aws-swf-image-processing-sample-workflow.png "AWS SWF demo workflow")


### 1. Register a domain.
  First, we need to register a domain.
  ```
    $ swafe register.domain ImageWorkflow 14 --desc 'Sample Image processing workflow'

      Registering domain ImageWorkflow
      Successfully registered ImageWorkflow
  ```

  The command **register.domain** takes two arguments and one option. Required arguments are the domain name (*ImageWorkflow*) and the workflow execution retention period in days (*14*). SWF allows a maximum retention period of 90 days.

  The *--desc* option allows you to attach a brief description to your domain.


### 2. Define your workflow

  Swafe provides classes and decorators that make it easier to define your workflows. The (simplified) code below shows a workflow definition.

  *Full examples can be found on this project's repo under `examples/`.*

  In your demo folder, create a file called `image_processing_workflow.py` and
  paste the code below.

  ```python
  from swafe.workflow import Workflow


  class ImageProcessingWorkflow(Workflow):
      domain = 'ImageProcessing'
      name = 'ImageProcessingWorkflow'
      taskList = 'ImageProcessingTaskList'
      version = '0.0.1'
      description = 'Image Processing Pipeline'

      # This is an abstract method that must be implemented in all
      # Workflow subclasses
      def decider(self, decision_task):
          pass
  ```

### 3. Register your workflow
  Once you've saved the file, run the following command in the same folder.

  ```
   $ swafe register.workflow image_processing_workflow.ImageProcessingWorkflow
     Registering workflow ImageProcessingWorkflow
     Successfully regisered workflow ImageProcessingWorkflow in ImageProcessing domain
  ```

  You've Successfully registered a workflow!
  The attributes defined are all necessary, always remember to update the version number if you're updating your workflow. This way, any active workflows won't be affected by the changes.

### Define your activities
  From the diagram above, our Workflow will have four tasks:
  1. S3Download
  2. SepiaTransform
  3. GrayscaleTransform
  4. S3Upload

We'll be using Pillow (PIL fork) for image transformation.

In order to get a sepia transform, we'll first have to transform the image to grayscale.
Our workflow will transform all images to grayscale (regardless of the transform) then optionally transform to sepia if the transform specified is sepia. If the transform is grayscale we won't do the sepia transform. The last activity is s3 upload.

Create an s3 bucket and upload the images you'd like to transform.

Update your `image_processing_workflow.py` as follows (*remember to replace <YOUR BUCKET> with your actual bucket name*):

```python
from swafe.workflow import Workflow
from swafe import activity
import boto3
import json
import os
from PIL import Image, ImageOps

class ImageProcessingWorkflow(Workflow):
    domain = 'ImageProcessing'
    name = 'ImageProcessingWorkflow'
    taskList = 'ImageProcessingTaskList'
    version = '0.0.1'
    description = 'Image Processing Pipeline'

    # This is an abstract method that must be implemented in all
    # Workflow subclasses
    def decider(self, decision_task):

        if decision_task.event_type == 'WorkflowExecutionStarted':
            return self._build_decisions(self.s3_download, decision_task.input)
        if decision_task.completed_activity == self.s3_download.name:
            return self._build_decisions(self.grayscale_transform, decision_task.input)
        if decision_task.completed_activity == self.grayscale_transform.name:
            image_data = json.loads(decision_task.input)
            if image_data['transform'] == 'sepia':
                return self._build_decisions(self.sepia_transform, decision_task.input)
            return self._build_decisions(self.s3_upload, decision_task.input)
        if decision_task.completed_activity == self.sepia_transform.name:
            return self._build_decisions(self.s3_upload, decision_task.input)
        return self._build_decisions()

    @activity.initialize(version='0.0.1')
    def s3_download(image_data):
        image_data = json.loads(image_data)

        s3 = boto3.client('s3')
        local_path = '%s/tmp/%s' % (os.path.dirname(os.path.realpath(__file__)),
                        image_data['path'].split('/')[-1])
        s3.download_file('<YOUR BUCKET>', image_data['path'], local_path)
        image_data['local_path'] = local_path
        return json.dumps(image_data)

    @activity.initialize(version='0.0.1')
    def grayscale_transform(image_data):
        image_data = json.loads(image_data)

        image = Image.open(image_data['local_path'])

        # convert to grayscale
        if image.mode != "L":
            image = image.convert("L")

        image.save(image_data['local_path'])

        return json.dumps(image_data)

    @activity.initialize(version='0.0.1')
    def sepia_transform(image_data):
        image_data = json.loads(image_data)

        # make sepia ramp (tweak color as necessary)
        sepia = []
        r, g, b = (255, 240, 192)
        for i in range(255):
            sepia.extend((r*i/255, g*i/255, b*i/255))

        image = Image.open(image_data['local_path'])

        # optional: apply contrast enhancement here, e.g.
        image = ImageOps.autocontrast(image)

        # apply sepia palette
        image.putpalette(sepia)

        # convert back to RGB so we can save it as JPEG
        # (alternatively, save it in PNG or similar)
        image = image.convert('RGB')

        image.save(image_data['local_path'])
        return json.dumps(image_data)

    @activity.initialize(version='0.0.1')
    def s3_upload(image_data):
        image_data = json.loads(image_data)

        s3 = boto3.client('s3')
        s3.upload_file(image_data['local_path'], '<YOUR BUCKET>', image_data['path'])
        return 'success'

```

Take a look at the `decider` function. The first line `if decision_task.event_type == 'WorkflowExecutionStarted'` is
the first step. When a workflow execution is started, a decision task of event type `WorkflowExecutionStarted` is sent.
Our decider checks for this attribute to determine if it's a new workflow execution and runs the first task, s3_download.
`return self._build_decisions(self.s3_download, decision_task.input)` starts the s3_download activity with the input provided
when the activity is started.

`if image_data['transform'] == 'sepia':` checks if the transform is sepia.

## Register your activities

Once you've saved your `image_processing_workflow.py` file, register your activities.

```
 $  swafe register.workflow.activities image_processing_workflow.ImageProcessingWorkflow
    Registering activities under ImageProcessingWorkflow
    Successfully registered activity grayscale_transform
    Successfully registered activity s3_download
    Successfully registered activity s3_upload
    Successfully registered activity sepia_transform
```
Your workflows are registered!

## Start your workflow

Now start your workflow.

```
 $  swafe decider image_processing_workflow.ImageProcessingWorkflow start
    Starting decider for ImageProcessingWorkflow
    PID file: swafe-imageprocessingworkflow.pid
    Stdout log: swafe-imageprocessingworkflow.log
    Stderr log: swafe-imageprocessingworkflow-error.log
    Starting...
```

The decider command takes two arguments: the decider class name (*image_processing_workflow.ImageProcessingWorkflow*) and the action (start, stop, restart)
It also takes an option --workers which allows you to set the number of workers to run. The default is 5.

The above command starts your decider and 5 activity workers. Activity workers are background threads that wait for activity executions.
The decider is also a background process that waits for decision tasks.

## Start a workflow execution.

Before you start a workflow execution, make sure you create a `tmp` directory in your project directory.

Run the following script:

```python
  from swafe.helpers import start_workflow
  from image_processing_workflow import ImageProcessingWorkflow
  import json

  workflow = ImageProcessingWorkflow()

  start_workflow(workflow.domain, workflow.type(), { 'name': workflow.taskList }, json.dumps({ 'path': '<PATH TO SAMPLE IMAGE ON S3>', 'transform': 'sepia' }))
```

If you check your `swafe-imageprocessingworkflow.log` you'll see the following output:

```
received decision task None
received activity task s3_download
result {"path": "raw-images/kilimanjaro.jpg", "local_path": "local/path/to/jpg", "transform": "sepia"}
received decision task s3_download
received activity task grayscale_transform
result {"path": "raw-images/kilimanjaro.jpg", "local_path": "local/path/to/jpg", "transform": "sepia"}
received decision task grayscale_transform
received activity task sepia_transform
result {"path": "raw-images/kilimanjaro.jpg", "local_path": "local/path/to/jpg", "transform": "sepia"}
received decision task sepia_transform
received activity task s3_upload
result success
received decision task s3_upload
```

If you change the transform to grayscale, i.e

```
  start_workflow(workflow.domain, workflow.type(), { 'name': workflow.taskList }, json.dumps({ 'path': '<PATH TO SAMPLE IMAGE ON S3>', 'transform': 'grayscale' }))
```

..your output will be as follows:

```
received decision task None
received activity task s3_download
result {"path": "raw-images/kilimanjaro.jpg", "local_path": "local/path/to/jpg", "transform": "grayscale"}
received decision task s3_download
received activity task grayscale_transform
result {"path": "raw-images/kilimanjaro.jpg", "local_path": "local/path/to/jpg", "transform": "grayscale"}
received decision task grayscale_transform
received activity task s3_upload
result success
received decision task s3_upload
```

And that's it, you have a running workflow!

## CLI Manual
  Swafe comes with a handy cli interface that allows you to manage your SWF workspace.

  ```
  $ swafe --help
    Usage: swafe [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      decider
      deprecate.domain
      deprecate.workflow
      describe.domain
      describe.workflow
      list.domain.workflows
      list.domains
      register.domain
      register.workflow
      register.workflow.activities
  ```
