class ExcecutionFailed(Exception):
    def __init__(self, exception, details=None):
        super(ExcecutionFailed, self).__init__('%s: %s' % (exception.__class__.__name__, str(exception)))
        self.details = details
