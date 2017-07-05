'''
Author: Ishuah Kariuki
This is a workflow demo.
The image processing functions defined here are borrowed from
http://effbot.org/zone/pil-sepia.htm
'''
from builtins import range
import json
import os
import boto3
from swafe.workflow import Workflow
from swafe import activity
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
        s3.download_file('swf-image-processing',
                         image_data['path'], local_path)
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
            sepia.extend((r*i//255, g*i//255, b*i//255))

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
        s3.upload_file(image_data['local_path'], 'swf-image-processing',
                       image_data['path'].replace('raw-images', 'processed-images'))
        return 'success'
