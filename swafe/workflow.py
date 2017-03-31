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
    tasks = []

    def __init__(self):
        _tasks = self.tasks
        self.tasks = {}
        self.__add_tasks(_tasks)

    def __add_tasks(self, tasks):
        for task in tasks:
            self.__add_task(task)

    def __add_task(self, task):
        if self.tasks:
            prev_task = self.tasks[self.tasks.keys()[-1]].func_name
            self.tasks[prev_task] = task
        else:
            self.tasks['start'] = task

    def next_task(self, prev_task='start'):
        return self.tasks[prev_task]

    def get_workflow_type(self):
        return { 'name': self.name, 'version': self.version }

    def get_params(self):
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
