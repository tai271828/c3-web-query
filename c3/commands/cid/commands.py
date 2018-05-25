import click
import c3.api.cids as cids

@click.command()
@click.option('--location',
              type=click.Choice(['taipei', 'beijing', 'lexington', 'all']),
              default='all',
              help='Show systems with the given location only')
@click.option('--certificate',
              type=click.Choice(['14.04.5', '16.04 LTS']),
              default='16.04',
              help='Filters to match certify status.')
@click.option('--enablement',
              type=click.Choice(['Enabled', 'Certified']),
              default='Enabled',
              help='Enabled(pre-installed), Certified(N+1).')
@click.option('--status',
              type=click.Choice(['Complete - Pass']),
              default='Complete - Pass',
              help='Certificate status')
def show_cid(location, certificate, enablement, status):
    """
    Create a test pool by given categories.
    """
    cids.get_cids(location, certificate, enablement, status)

