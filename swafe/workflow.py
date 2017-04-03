from activity import Activity


class Workflow(object):
    domain = None
    name = None
    version = None
    taskList = None
    description = None
    taskStartToCloseTimeout = None
    executionStartToCloseTimeout = None
    taskPriority = None
    childPolicy = None
    lambdaRole = None

    def type(self):
        return { 'name': self.name, 'version': self.version }

    def params(self):
        params = dict(domain=self.domain, name=self.name, version=self.version)
        if self.description:
            params['description'] = self.description
        if self.taskStartToCloseTimeout:
            params['defaultTaskStartToCloseTimeout'] = self.taskStartToCloseTimeout
        if self.executionStartToCloseTimeout:
            params['defaultExecutionStartToCloseTimeout'] = self.executionStartToCloseTimeout
        if self.taskList:
            params['defaultTaskList'] = { 'name': self.taskList }
        if self.taskPriority:
            params['defaultTaskPriority'] = self.taskPriority
        if self.childPolicy:
            params['defaultChildPolicy'] = self.childPolicy
        if self.lambdaRole:
            params['defaultLambdaRole'] = self.lambdaRole

        return params

    def activity_definitions(self):
        return [getattr(self, func).params() for func in dir(self) if isinstance(getattr(self, func), Activity)]
