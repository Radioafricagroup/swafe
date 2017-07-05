from swafe.workflow import Workflow
from swafe import activity
import boto3
import uuid
from builtins import str
from swafe.helpers import start_workflow
from swafe.task import DecisionTask


TEST_DOMAIN_PARAMS = { 'name': 'CLITestCaseDomain',
          'workflowExecutionRetentionPeriodInDays': '14', 'description': 'Test Domain' }

TEST_WORKFLOW_CLASSPATH = 'swafe.tests.mocker.TestCaseWorkflow'

def setup_mock_env():
    swf = boto3.client('swf')
    test_workflow = TestCaseWorkflow()

    register_mock_domain(TEST_DOMAIN_PARAMS)
    swf.register_workflow_type(**test_workflow.params())

    for activity_definition in test_workflow.activity_definitions():
        activity_definition['domain'] = test_workflow.domain
        activity_definition['defaultTaskList'] = {
            'name': test_workflow.taskList}

        swf.register_activity_type(**activity_definition)

def register_mock_domain(domain):
    swf = boto3.client('swf')
    swf.register_domain(**domain)

def setup_mock_decision():
    swf = boto3.client('swf')

    test_workflow = TestCaseWorkflow()

    swf.start_workflow_execution(
        domain=test_workflow.domain,
        workflowId='ingestion-'+str(uuid.uuid4()),
        workflowType=test_workflow.type(),
        taskList={'name': test_workflow.taskList},
        input='mock data'
    )

def setup_mock_activity():
    setup_mock_decision()

    swf = boto3.client('swf')
    test_workflow = TestCaseWorkflow()

    task = swf.poll_for_decision_task(
        domain=test_workflow.domain,
        taskList={'name': test_workflow.taskList},
        identity='decider-%s-%s' % (test_workflow.name, str(uuid.uuid4()))
    )
    decision_task = DecisionTask(task)

    decisions = test_workflow.decider(decision_task)

    swf.respond_decision_task_completed(
        taskToken=decision_task.task_token, decisions=decisions)



class TestCaseWorkflow(Workflow):
    domain = 'CLITestCaseDomain'
    name = 'CLITestCaseWorkflow'
    taskList = 'TaskList'
    version = '4.0.4'
    description = 'Test Case Workflow'

    def decider(self, decision_task):
        if decision_task.event_type == 'WorkflowExecutionStarted':
            return self._build_decisions(self.test_activity_one, decision_task.input)
        return self._build_decisions()

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
