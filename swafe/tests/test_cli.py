import unittest
import boto3
from moto import mock_swf
import click
from click.testing import CliRunner
from swafe import cli
from .mocker import *


class CLITestCase(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.mock_swf = mock_swf()
        self.mock_swf.start()

        self.test_workflow = TestCaseWorkflow()


        setup_mock_env()

    def tearDown(self):
        self.mock_swf.stop()

    def test_list_domains(self):
        result = self.runner.invoke(cli.list_domains)
        self.assertEqual(result.exit_code, 0)
        self.assertIn(TEST_DOMAIN_PARAMS['name'], result.output)

    def test_describe_domain(self):
        result = self.runner.invoke(cli.describe_domain, [TEST_DOMAIN_PARAMS['name']])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('status: REGISTERED', result.output)

        result = self.runner.invoke(cli.describe_domain, ['Non-ExistentDomain'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Unknown domain: Non-ExistentDomain', result.output)

    def test_register_domain(self):
        test_domain_args = ['CLITestCaseDomain2', '14', '--desc', 'test domain']
        result=self.runner.invoke(cli.register_domain, test_domain_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully registered %s' % test_domain_args[0], result.output)

        result=self.runner.invoke(cli.register_domain, test_domain_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('DomainAlreadyExistsFault', result.output)

    def test_deprecate_domain(self):
        result=self.runner.invoke(cli.deprecate_domain, [TEST_DOMAIN_PARAMS['name']])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully deprecated %s' % TEST_DOMAIN_PARAMS['name'], result.output)

        result=self.runner.invoke(cli.deprecate_domain, [TEST_DOMAIN_PARAMS['name']])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('DomainDeprecatedFault', result.output)

    def test_list_domain_workflows(self):
        result=self.runner.invoke(cli.list_domain_workflows, [TEST_DOMAIN_PARAMS['name'], '--name', 'Non-ExistentWorflow'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(self.test_workflow.name, result.output)

        register_mock_domain({ 'name': 'WorkflowLessDomain',
            'workflowExecutionRetentionPeriodInDays': '14',
            'description': 'Test Domain'})

        result=self.runner.invoke(cli.list_domain_workflows, ['WorkflowLessDomain'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('There are no REGISTERED workflows', result.output)

        result=self.runner.invoke(cli.list_domain_workflows, ['Non-ExistentDomain'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('UnknownResourceFault', result.output)

    def test_describe_workflow(self):
        result = self.runner.invoke(cli.describe_workflow, [TEST_WORKFLOW_CLASSPATH])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('REGISTERED', result.output)
        self.assertIn('description:', result.output)

        result = self.runner.invoke(cli.describe_workflow, ['swafe.tests.mocker.TestCaseWorkflow1'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('UnknownResourceFault', result.output)

    def test_register_workflow(self):
        result = self.runner.invoke(cli.register_workflow, ['swafe.tests.mocker.TestCaseWorkflow1'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully registered workflow CLITestCaseWorkflow1', result.output)

        result = self.runner.invoke(cli.register_workflow, [TEST_WORKFLOW_CLASSPATH])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('TypeAlreadyExistsFault', result.output)

    def test_deprecate_workflow(self):
        result = self.runner.invoke(cli.deprecate_workflow, [TEST_WORKFLOW_CLASSPATH])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully deprecated %s' % self.test_workflow.name, result.output)

        result = self.runner.invoke(cli.deprecate_workflow, [TEST_WORKFLOW_CLASSPATH])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('TypeDeprecatedFault', result.output)

    def test_register_activities(self):
        result = self.runner.invoke(cli.register_activities, [TEST_WORKFLOW_CLASSPATH])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('test_activity_two', result.output)
