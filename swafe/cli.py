import click
from lib import swf
from botocore.exceptions import ClientError

@click.group()
@click.pass_context
def run(context):
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
        print e.response['Error']['Message']
        return

    click.echo('- %s' % domain)
    click.echo('\t description: %s' % response['domainInfo']['description'])
    click.echo('\t status: %s' % response['domainInfo']['status'])
    click.echo('\t retention perion: %s' % response['configuration']['workflowExecutionRetentionPeriodInDays'])

@run.command('register.domain')
@click.argument('domain', required=True)
@click.argument('retention_period', required=True)
@click.option('--desc', help='Short description of the domain')
def register_domain(domain, retention_period, desc):
    click.echo('Registering domain %s' % domain)

    try:
        response = swf.register_domain(name=domain, description=desc, workflowExecutionRetentionPeriodInDays=retention_period)
    except ClientError as e:
        print e.response['Error']['Code'], e.response['Error']['Message']
        return

    click.echo('Successfully registered %s ' % domain)

@run.command('deprecate.domain')
@click.argument('domain', required=True)
def deprecate_domain(domain):
    click.echo('Deprecating domain %s' % domain)

    try:
        response = swf.deprecate_domain(name=domain)
    except ClientError as e:
        print e.response['Error']['Code'], e.response['Error']['Message']
        return

    click.echo('Successfully deprecated %s ' % domain)
