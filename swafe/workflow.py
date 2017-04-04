from activity import Activity
import abc


class Workflow(object):
    domain = None
    name = None
    version = None
    taskList = None
    description = None
    taskStartToCloseTimeout = 'NONE'
    executionStartToCloseTimeout = '3600'
    taskPriority = None
    childPolicy = 'TERMINATE'
    lambdaRole = None

    __metaclass__ = abc.ABCMeta

    def type(self):
        return { 'name': self.name, 'version': self.version }

    def params(self):
        params = dict(domain=self.domain, name=self.name, version=self.version)
        params['defaultTaskStartToCloseTimeout'] = self.taskStartToCloseTimeout
        params['defaultExecutionStartToCloseTimeout'] = self.executionStartToCloseTimeout
        params['defaultChildPolicy'] = self.childPolicy

        if self.description:
            params['description'] = self.description
        if self.taskList:
            params['defaultTaskList'] = { 'name': self.taskList }
        if self.taskPriority:
            params['defaultTaskPriority'] = self.taskPriority
        if self.lambdaRole:
            params['defaultLambdaRole'] = self.lambdaRole

        return params

    def activity_definitions(self):
        return [getattr(self, func).params() for func in dir(self) if isinstance(getattr(self, func), Activity)]

    @abc.abstractmethod
    def decider(self, decision_task):
        raise NotImplementedError('subclasses should implement this method')
