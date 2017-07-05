import unittest
import boto3
from moto import mock_swf
from swafe import poller
from .mocker import *


class PollerTestCase(unittest.TestCase):

    def setUp(self):
        self.mock = mock_swf()
        self.mock.start()
        self.test_workflow = TestCaseWorkflow()

        setup_mock_env()


    def tearDown(self):
        self.mock.stop()

    def test_poll_for_decision_task(self):
        setup_mock_decision()
        
        task = poller.poll_for_decision_task(
            self.test_workflow.domain, {'name': self.test_workflow.taskList},
            self.test_workflow.name)

        if 'taskToken' not in task:
            self.fail('No decisions found after poll')

        self.assertEqual(task['workflowType'], self.test_workflow.type())

    def test_poll_for_activity_task(self):
        setup_mock_activity()

        task = poller.poll_for_activity_task(
            self.test_workflow.domain, { 'name': self.test_workflow.taskList },
            self.test_workflow.name)

        if 'taskToken' not in task:
            self.fail('No activities found after poll')

        self.assertEqual(task['activityType']['name'], 'test_activity_one')
