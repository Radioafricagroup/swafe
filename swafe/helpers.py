from __future__ import print_function
from __future__ import absolute_import
from builtins import str
import uuid
from botocore.exceptions import ClientError
from .lib import swf


def start_workflow(domain, workflowType, taskList, activity_input):
    try:
        response = swf.start_workflow_execution(
            domain=domain,
            workflowId='ingestion-'+str(uuid.uuid4()),
            workflowType=workflowType,
            taskList=taskList,
            input=activity_input
        )
        print("Workflow requested: ", response)
    except ClientError as error:
        print("Workflow excecution already started: ",
              error.response.get("Error", {}).get("Code"))
