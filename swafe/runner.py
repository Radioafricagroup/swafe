from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from . import poller
from botocore.vendored.requests.exceptions import ReadTimeout
from botocore.exceptions import ClientError
from .task import ActivityTask, DecisionTask
from .exceptions import ActivityFailed, WorkflowFailed
from .lib import swf
from .daemon import Daemon
from threading import Thread
from multiprocessing.pool import ThreadPool
import logging


class Worker(Thread):
    def __init__(self, workflow, logger):
        Thread.__init__(self)
        self.workflow = workflow
        self.logger = logger
        self.daemon = True
        self.start()
        self.logger.debug('Started thread')


    def run(self):
        while True:
            try:
                task = poller.poll_for_activity_task(
                    self.workflow.domain, {'name': self.workflow.taskList}, self.workflow.name)
                # Check if poll is empty
                if not 'taskToken' in task:
                    self.logger.debug("No activities found after poll")
                    continue

                activity_task = ActivityTask(task)
                self.logger.debug('Received task \'%s\' with id: %s' % (activity_task.activity, activity_task.activity_id))
                activity = getattr(self.workflow, activity_task.activity)
                result = activity.action(activity_task.input)

                swf.respond_activity_task_completed(
                    taskToken=activity_task.task_token, result=result)
                self.logger.debug('Completed task \'%s\' with id: %s' % (activity_task.activity, activity_task.activity_id))
            except ReadTimeout as e:
                self.logger.error('Read timeout while polling')
            except ClientError as e:
                self.logger.error(e)
            except ActivityFailed as e:
                self.logger.error(e)
                swf.respond_activity_task_failed(
                    taskToken=activity_task.task_token, reason=str(e), details=e.details)
            except Exception as e:
                self.logger.error(e)


class Decider(Daemon):

    def __init__(self, workflow, pidfile, stdout, stderr, worker_count=5):
        super(Decider, self).__init__(pidfile, stdout, stderr)
        self.workflow = workflow
        self.worker_count = worker_count

    def run(self):
        for _ in range(self.worker_count):
            Worker(self.workflow, self.logger)
        while True:
            try:
                task = poller.poll_for_decision_task(
                    self.workflow.domain, {'name': self.workflow.taskList}, self.workflow.name)

                # Check if poll is empty
                if not 'taskToken' in task:
                    self.logger.debug("No decisions found after poll")
                    continue

                decision_task = DecisionTask(task)

                if decision_task.completed_activity:
                    self.logger.debug('Received %s, workflowId: %s, activity: %s, activityId: %s' %
                    (decision_task.event_type,
                        decision_task.workflow_id,
                        decision_task.completed_activity,
                        decision_task.completed_activity_id))
                else:
                    self.logger.debug('Received %s, workflowId: %s' % (decision_task.event_type, decision_task.workflow_id))

                decisions = self.workflow.decider(decision_task)
                swf.respond_decision_task_completed(
                    taskToken=decision_task.task_token, decisions=decisions)

                for decision in decisions:
                    if decision['decisionType'] == 'ScheduleActivityTask':
                        self.logger.debug('Dispatched %s, activity: %s, activityId: %s, workflowId: %s' %
                        (decision['decisionType'],
                            decision['scheduleActivityTaskDecisionAttributes']['activityType']['name'],
                            decision['scheduleActivityTaskDecisionAttributes']['activityId'],
                            decision_task.workflow_id))
                    elif decision['decisionType'] == 'CompleteWorkflowExecution':
                        self.logger.debug('Completed workflow execution, workflowId: %s' %
                            decision_task.workflow_id)

            except ReadTimeout as e:
                self.logger.error("Read timeout while polling", e)
            except ClientError as e:
                self.logger.error("Client error", e)
            except WorkflowFailed as e:
                self.logger.error(e)
                swf.respond_decision_task_completed([
                    {
                        'decisionType': 'FailWorkflowExecution',
                        'failWorkflowExecutionDecisionAttributes': {
                            'reason': e.reason,
                            'detail': e.details
                        }
                    }
                ])
