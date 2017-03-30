import click
from lib import swf

@click.group()
@click.pass_context
def run(context):
    pass

@run.command()
@click.option('--registered/--deprecated', default=True,
                help='Specify the registration status of the domains to list, default is REGISTERED')
def list_domains(registered):
    status = 'REGISTERED' if registered else 'DEPRECATED'

    click.echo('Fetching %s domains...' % status)
    response = swf.list_domains(registrationStatus=status,
                                maximumPageSize=100)

    if len(response['domainInfos']) == 0:
        click.echo('There are no %s domains' % status)
    for domain in response['domainInfos']:
        click.echo(' - %s' % domain['name'])
