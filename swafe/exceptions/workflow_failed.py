class WorkflowFailed(Exception):
    def __init__(self, reason,details=None):
        super(WorkflowFailed, self).__init__('%s' % reason)
        self.reason = reason
        self.details = details
