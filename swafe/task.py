from exceptions import MalformedTask

class DecisionTask(object):

    def __init__(self, task_json):
        if 'taskToken' in task_json:
            self.task_token = task_json['taskToken']
        else:
            raise MalformedTask("invalid task, missing taskToken")

        self.history = [evt for evt in task_json['events']
                        if not evt['eventType'].startswith('Decision')]

        self.completed_activity = None
        last_event = self.history[-1]
        self.event_type = last_event['eventType']

        if last_event['eventType'] == 'WorkflowExecutionStarted' and task_json['taskToken'] not in self.history:
            self.input = last_event[
                'workflowExecutionStartedEventAttributes']['input']
        elif last_event['eventType'] == 'ActivityTaskCompleted':
            completed_activity_id = last_event[
                'activityTaskCompletedEventAttributes']['scheduledEventId'] - 1
            self.completed_activity = task_json['events'][completed_activity_id][
                'activityTaskScheduledEventAttributes']['activityType']['name']
            self.input = last_event[
                'activityTaskCompletedEventAttributes'].get('result')
        elif last_event['eventType'] == 'ActivityTaskFailed':
            self.reason = last_event['activityTaskFailedEventAttributes']['reason']
            self.details = last_event['activityTaskFailedEventAttributes']['details']


class ActivityTask(object):

    def __init__(self, task_json):
        if 'taskToken' in task_json:
            self.task_token = task_json['taskToken']
        else:
            raise MalformedTask("invalid task, missing task Token")

        self.activity = task_json['activityType']['name']
        self.activity_version = task_json['activityType']['version']
        self.input = task_json['input']
