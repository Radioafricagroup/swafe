import click
import os
import sys
from lib import swf
from botocore.exceptions import ClientError
from runner import Runner


@click.group()
@click.pass_context
def run(context):
    sys.path.append(os.getcwd())
    pass


@run.command('list.domains')
@click.option('--registered/--deprecated', default=True,
              help='Specify the registration status of the domains to list, default is REGISTERED')
def list_domains(registered):
    status = 'REGISTERED' if registered else 'DEPRECATED'

    click.echo('Fetching %s domains...' % status)
    response = swf.list_domains(registrationStatus=status)

    if len(response['domainInfos']) == 0:
        click.echo('There are no %s domains' % status)
        return

    for domain in response['domainInfos']:
        click.echo(' - %s' % domain['name'])


@run.command('describe.domain')
@click.argument('domain', required=True)
def describe_domain(domain):
    click.echo('Fetching details for %s' % domain)

    try:
        response = swf.describe_domain(name=domain)
    except ClientError as e:
        click.echo(e.response['Error']['Message'])
        return

    click.echo('- %s' % domain)
    if response['domainInfo'].has_key('description'):
        click.echo('\t description: %s' %
                   response['domainInfo']['description'])
    click.echo('\t status: %s' % response['domainInfo']['status'])
    click.echo('\t retention perion: %s' % response['configuration'][
               'workflowExecutionRetentionPeriodInDays'])


@run.command('register.domain')
@click.argument('domain', required=True)
@click.argument('retention_period', required=True)
@click.option('--desc', help='Short description of the domain')
def register_domain(domain, retention_period, desc):
    click.echo('Registering domain %s' % domain)
    params = {'name': domain,
              'workflowExecutionRetentionPeriodInDays': retention_period}
    if desc:
        params['description'] = desc
    try:
        response = swf.register_domain(**params)
    except ClientError as e:
        click.echo('%s %s' % (e.response['Error']['Code'], e.response['Error']['Message']))
        return

    click.echo('Successfully registered %s ' % domain)


@run.command('deprecate.domain')
@click.argument('domain', required=True)
def deprecate_domain(domain):
    click.echo('Deprecating domain %s' % domain)
    try:
        response = swf.deprecate_domain(name=domain)
    except ClientError as e:
        click.echo('%s %s ' % (e.response['Error']['Code'], e.response['Error']['Message']))
        return

    click.echo('Successfully deprecated %s ' % domain)


@run.command('list.domain.workflows')
@click.argument('domain', required=True)
@click.option('--registered/--deprecated', default=True, help='Specify the registration status of the workflows to list, default is REGISTERED')
@click.option('--name', help='If specified, lists the workflow type with this name')
def list_domain_workflows(domain, registered, name):
    status = 'REGISTERED' if registered else 'DEPRECATED'
    click.echo('Fetching %s worflows in the domain %s ' % (status, domain))
    params = dict(domain=domain, registrationStatus=status)
    if name:
        params['name'] = name
    try:
        response = swf.list_workflow_types(**params)
    except ClientError as e:
        click.echo('%s %s' % (e.response['Error']['Code'], e.response['Error']['Message']))
        return
    if len(response['typeInfos']) == 0:
        if name:
            click.echo('There are no %s workflows with the name %s in the domain %s' % (
                status, name, domain))
            return
        click.echo('There are no %s workflows in the domain %s ' %
                   (status, domain))
        return

    click.echo('Domain: %s \n' % domain)

    for workflow in response['typeInfos']:
        click.echo(' %s - (version %s)' %
                   (workflow['workflowType']['name'], workflow['workflowType']['version']))
        click.echo('\t status: %s' % workflow['status'])
        if workflow.has_key('description'):
            click.echo('\t description: %s' % workflow['description'])
        click.echo('\t created: %s \n' % workflow['creationDate'])


@run.command('describe.workflow')
@click.argument('workflowClassPath', required=True)
def describe_workflow(workflowclasspath):

    workflow = instantiate_class(workflowclasspath)
    click.echo('Fetching workflow %s' % workflow.name)
    try:
        response = swf.describe_workflow_type(domain=workflow.domain,
                                              workflowType=workflow.type())
    except ClientError as e:
        click.echo('%s %s ' % (e.response['Error']['Code'], e.response['Error']['Message']))
        return

    click.echo(workflow.name)
    click.echo('\t status: %s' % response['typeInfo']['status'])
    click.echo('\t created:  %s' % response['typeInfo']['creationDate'])

    if response['configuration'].has_key('description'):
        click.echo('\t description: %s ' %
                   response['configuration']['description'])


@run.command('register.workflow')
@click.argument('workflowClassPath', required=True)
def register_workflow(workflowclasspath):

    workflow = instantiate_class(workflowclasspath)
    click.echo('Registering workflow %s' % workflow.name)
    try:
        response = swf.register_workflow_type(**workflow.params())
    except ClientError as e:
        click.echo('%s %s' % (e.response['Error']['Code'], e.response['Error']['Message']))
        return
    click.echo('Successfully regisered workflow %s in %s domain' %
               (workflow.name, workflow.domain))


@run.command('deprecate.workflow')
@click.argument('workflowClassPath', required=True)
def deprecate_workflow(workflowclasspath):
    workflow = instantiate_class(workflowclasspath)
    click.echo('Deprecating workflow %s ' % workflow.name)
    try:
        response = swf.deprecate_workflow_type(domain=workflow.domain,
                                               workflowType=workflow.type())
    except ClientError as e:
        click.echo('%s %s' % (e.response['Error']['Code'], e.response['Error']['Message']))
        return
    click.echo('Successfully deprecated %s ' % workflow.name)


@run.command('register.workflow.activities')
@click.argument('workflowClassPath', required=True)
def register_activities(workflowclasspath):
    workflow = instantiate_class(workflowclasspath)
    click.echo('Registering activities under %s ' % workflow.name)

    for activity_definition in workflow.activity_definitions():
        try:
            activity_definition['domain'] = workflow.domain
            activity_definition['defaultTaskList'] = {
                'name': workflow.taskList}

            swf.register_activity_type(**activity_definition)
            click.echo('Successfully registered activity %s ' %
                       activity_definition['name'])
        except ClientError as e:
            click.echo('%s %s ' % (e.response['Error']['Code'], e.response['Error']['Message']))


@run.command('decider')
@click.argument('workflowClassPath', required=True)
@click.argument('action', required=True)
@click.option('--workers', default=5, help='Number of workers to run, default is 5')
def run_decider(workflowclasspath, action, workers):
    workflow = instantiate_class(workflowclasspath)
    if workers < 1:
        click.echo('Number of workers cannot be less than 1')
        return
    pid_file = '%s/swafe-%s.pid' % (os.getcwd(), workflow.name.lower())
    stdout = '%s/swafe-%s.log' % (os.getcwd(), workflow.name.lower())
    stderr = '%s/swafe-%s-error.log' % (os.getcwd(), workflow.name.lower())
    runner = Runner(
        workflow, pid_file, stdout, stderr, workers)
    if action == 'start':
        click.echo('Starting decider for %s' % workflow.name)
        click.echo('PID file: %s' % pid_file)
        click.echo('Stdout log: %s' % stdout)
        click.echo('Stderr log: %s' % stderr)
        runner.start()
    elif action == 'stop':
        click.echo('Stopping decider for %s' % workflow.name)
        runner.stop()
    elif action == 'restart':
        click.echo('Restarting decider for %s' % workflow.name)
        click.echo('PID file: %s' % pid_file)
        click.echo('Stdout log: %s' % stdout)
        click.echo('Stderr log: %s' % stderr)
        runner.restart()
    else:
        click.echo(
            'Invalid action %s. Valid actions are start, stop and restart', action)


def instantiate_class(classpath):
    modulename, classname = classpath.rsplit('.', 1)
    module = __import__(modulename, fromlist=['*'])
    cls = getattr(module, classname)
    return cls()
