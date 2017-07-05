from __future__ import absolute_import
from builtins import object
from .exceptions import WorkflowFailed


class DecisionTask(object):

    def __init__(self, task_json):
        self.task_token = task_json['taskToken']
        self.history = [evt for evt in task_json['events']
                        if not evt['eventType'].startswith('Decision')]

        self.completed_activity = None
        self.completed_activity_id = None
        last_event = self.history[-1]
        self.event_type = last_event['eventType']
        self.workflow_id = task_json['workflowExecution']['workflowId']
        self.run_id = task_json['workflowExecution']['runId']

        if last_event['eventType'] == 'WorkflowExecutionStarted' and task_json['taskToken'] not in self.history:
            self.input = last_event[
                'workflowExecutionStartedEventAttributes']['input']
        elif last_event['eventType'] == 'ActivityTaskCompleted':
            completed_activity_index = last_event[
                'activityTaskCompletedEventAttributes']['scheduledEventId'] - 1
            self.completed_activity = task_json['events'][completed_activity_index][
                'activityTaskScheduledEventAttributes']['activityType']['name']
            self.completed_activity_id = task_json['events'][completed_activity_index][
                'activityTaskScheduledEventAttributes']['activityId']
            self.input = last_event[
                'activityTaskCompletedEventAttributes'].get('result')
        elif last_event['eventType'] == 'ActivityTaskFailed':
            raise WorkflowFailed(last_event['activityTaskFailedEventAttributes'][
                'reason'], last_event['activityTaskFailedEventAttributes']['details'])


class ActivityTask(object):

    def __init__(self, task_json):
        self.task_token = task_json['taskToken']

        self.activity_id = task_json['activityId']
        self.activity = task_json['activityType']['name']
        self.activity_version = task_json['activityType']['version']
        self.input = task_json['input']
