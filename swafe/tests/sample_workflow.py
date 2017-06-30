from swafe.workflow import Workflow
from swafe import activity


class TestCaseWorkflow(Workflow):
    domain = 'CLITestCaseDomain'
    name = 'CLITestCaseWorkflow'
    taskList = 'TaskList'
    version = '4.0.4'
    description = 'Test Case Workflow'

    def decider(self, decision_task):
        pass

    @activity.initialize(version='0.0.1')
    def test_activity_one(data):
        return 'analysis done | %s' % data

    @activity.initialize(version='0.0.1')
    def test_activity_two(data):
        return 'saving | %s' % data


class TestCaseWorkflow1(Workflow):
    domain = 'CLITestCaseDomain'
    name = 'CLITestCaseWorkflow1'
    taskList = 'TaskList'
    version = '4.0.4'
    description = 'Test Case Workflow'

    def decider(self, decision_task):
        pass
