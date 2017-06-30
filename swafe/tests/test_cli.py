import unittest
import boto3
from moto import mock_swf
import click
from click.testing import CliRunner
from swafe import cli
from .sample_workflow import TestCaseWorkflow


class CLITestCase(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.mock = mock_swf()
        self.mock.start()

        swf = boto3.client('swf')
        self.test_domain_params = { 'name': 'CLITestCaseDomain',
                  'workflowExecutionRetentionPeriodInDays': '14', 'description': 'Test Domain' }
        self.test_workflow_classpath = 'swafe.tests.sample_workflow.TestCaseWorkflow'
        self.test_workflow = TestCaseWorkflow()

        swf.register_domain(**self.test_domain_params)
        swf.register_workflow_type(**self.test_workflow.params())

    def tearDown(self):
        self.mock.stop()

    def test_list_domains(self):
        result = self.runner.invoke(cli.list_domains)
        self.assertEqual(result.exit_code, 0)
        self.assertIn(self.test_domain_params['name'], result.output)

    def test_describe_domain(self):
        result = self.runner.invoke(cli.describe_domain, [self.test_domain_params['name']])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('status: REGISTERED', result.output)

    def test_register_domain(self):
        test_domain_args = ['CLITestCaseDomain2', '14', '--desc', 'test domain']
        result = self.runner.invoke(cli.register_domain, test_domain_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully registered %s' % test_domain_args[0], result.output)

    def test_deprecate_domain(self):
        result = self.runner.invoke(cli.deprecate_domain, [self.test_domain_params['name']])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully deprecated %s' % self.test_domain_params['name'], result.output)

    def test_list_domain_workflows(self):
        result = self.runner.invoke(cli.list_domain_workflows, [self.test_domain_params['name']])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(self.test_workflow.name, result.output)

    def test_describe_workflow(self):
        result = self.runner.invoke(cli.describe_workflow, [self.test_workflow_classpath])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('REGISTERED', result.output)

    def test_register_workflow(self):
        result = self.runner.invoke(cli.register_workflow, ['swafe.tests.sample_workflow.TestCaseWorkflow1'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully registered workflow CLITestCaseWorkflow1', result.output)

    def test_deprecate_workflow(self):
        result = self.runner.invoke(cli.deprecate_workflow, [self.test_workflow_classpath])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully deprecated %s' % self.test_workflow.name, result.output)

    def test_register_activities(self):
        result = self.runner.invoke(cli.register_activities, [self.test_workflow_classpath])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('test_activity_two', result.output)
