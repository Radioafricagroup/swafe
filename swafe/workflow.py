# -*- coding: utf-8 -*-
"""Worflow module

This module contains the workflow class that defines an SWF workflow.
"""
from __future__ import absolute_import
from builtins import str
from builtins import object
import abc
import uuid
from future.utils import with_metaclass
from .activity import Activity


class Workflow(with_metaclass(abc.ABCMeta, object)):
    """A workflow class definition

    This class contains all the neccesary fields and methods for seamless
    SWF workflow creation and execution
    """
    domain = None
    name = None
    version = None
    taskList = None
    description = None
    taskStartToCloseTimeout = '3600'
    executionStartToCloseTimeout = '3600'
    taskPriority = None
    childPolicy = 'TERMINATE'
    lambdaRole = None

    def type(self):
        """Returns a dict with workflow name and version.
        SWF Workflow type is expected in this format
        """
        return {'name': self.name, 'version': self.version}

    def params(self):
        """Returns a dict with Workflow params neccesary for workflow
        registration
        """
        params = dict(domain=self.domain, name=self.name, version=self.version)
        params['defaultTaskStartToCloseTimeout'] = self.taskStartToCloseTimeout
        params['defaultExecutionStartToCloseTimeout'] = self.executionStartToCloseTimeout
        params['defaultChildPolicy'] = self.childPolicy

        if self.description:
            params['description'] = self.description
        if self.taskList:
            params['defaultTaskList'] = {'name': self.taskList}
        if self.taskPriority:
            params['defaultTaskPriority'] = self.taskPriority
        if self.lambdaRole:
            params['defaultLambdaRole'] = self.lambdaRole

        return params

    def activity_definitions(self):
        """Returns a list of activity names
        An activity is any function defined in the workflow class
        with an @activity decorator
        """
        return [getattr(self, func).params()
                for func in dir(self) if isinstance(getattr(self, func),
                                                    Activity)]

    def _build_decisions(self, activity=None, activity_input=''):
        """Returns a list of decisions as expected by the function
        boto3.client('swf').respond_decision_task_completed
        """
        if activity:
            return [
                {
                    'decisionType': 'ScheduleActivityTask',
                    'scheduleActivityTaskDecisionAttributes': {
                        'activityType': {
                            'name': activity.name,
                            'version': activity.version
                        },
                        'activityId': 'activity-%s-%s'
                                      % (activity.name, str(uuid.uuid4())),
                        'input': activity_input,
                        'scheduleToCloseTimeout': 'NONE',
                        'scheduleToStartTimeout': 'NONE',
                        'startToCloseTimeout': 'NONE',
                        'heartbeatTimeout': '3600',
                        'taskList': {'name': self.taskList},
                    }
                }
            ]
        return [
            {
                'decisionType': 'CompleteWorkflowExecution',
                'completeWorkflowExecutionDecisionAttributes': {
                    'result': 'success'
                }
            }
        ]

    @abc.abstractmethod
    def decider(self, decision_task):
        """This method should be implemented by all subclasses
        """
        raise NotImplementedError('subclasses should implement this method')
