from lib import swf
import uuid


def poll_for_decision_task(workflow):
    return swf.poll_for_decision_task(
        domain=workflow.domain,
        taskList={ 'name': workflow.taskList }
        identity='decider-%s-%s' % (workflow.name, str(uuid.uuid4()))
        )

def poll_for_activity_task(workflow):
    return swf.poll_for_activity_task(
        domain=workflow.domain,
        taskList={ 'name': workflow.taskList }
        identity='worker-%s-%s' % (workflow.name, str(uuid.uuid4()))
        )
