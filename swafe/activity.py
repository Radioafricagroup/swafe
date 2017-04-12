def initialize(version):

    def wrap(func):
        return Activity(func, version)
    return wrap


class Activity(object):

    def __init__(self, func, version):
        self.name = func.__name__
        self.action = func
        self.version = version

    def params(self):
        return dict(version=self.version, name=self.name)
