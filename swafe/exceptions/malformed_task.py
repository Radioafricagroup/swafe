class MalformedTask(Exception):
    def __init__(self, message):
        super(MalformedTask, self).__init__(message)
