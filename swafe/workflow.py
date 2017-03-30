class Workflow(object):
    name = None
    task_list = None
    version = None
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