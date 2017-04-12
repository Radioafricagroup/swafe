from lib import swf
import uuid


def poll_for_decision_task(domain, task_list, workflow_name):
    return swf.poll_for_decision_task(
        domain=domain,
        taskList=task_list,
        identity='decider-%s-%s' % (workflow_name, str(uuid.uuid4()))
    )


def poll_for_activity_task(domain, task_list, workflow_name):
    return swf.poll_for_activity_task(
        domain=domain,
        taskList=task_list,
        identity='worker-%s-%s' % (workflow_name, str(uuid.uuid4()))
    )
