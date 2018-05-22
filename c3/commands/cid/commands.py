import click
import c3.api.cids as cids

@click.command()
@click.option('--location',
              type=click.Choice(['taipei', 'beijing', 'lexington', 'all']),
              default='all',
              help='Show systems with the given location only')
@click.option('--certificate',
              type=click.Choice(['14.04.5', '16.04']),
              default='16.04',
              help='Filters to match certify status.')
@click.option('--enablement',
              type=click.Choice(['Enabled', 'Certified']),
              default='Enabled',
              help='Enabled(pre-installed), Certified(N+1).')
def show_cid(location, certificate, enablement):
    """
    Create a test pool by given categories.
    """
    cids.go()
    #pass

