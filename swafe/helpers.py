import uuid
from lib import swf
from botocore.exceptions import ClientError

def start_workflow(domain, workflowType, taskList, activity_input):
    try:
        response = swf.start_workflow_execution(
            domain=domain,
            workflowId='ingestion-'+str(uuid.uuid4()),
            workflowType=workflowType,
            taskList=taskList,
            input=activity_input
        )
        print "Workflow requested: ", response
    except ClientError as e:
        print "Workflow excecution already started: ", e.response.get("Error", {}).get("Code")
