import click
import c3.api.cids as cids
import c3.io.csv as c3csv


@click.command()
@click.option('--component',
              type=click.Choice(['cpu', 'wifi', 'dkms', 'all']),
              default='all',
              help='The top concern of diversity of the pool.')
@click.option('--certificate',
              type=click.Choice(['14.04.5', '16.04']),
              default='16.04',
              help='Filters to match certify status.')
def create_prototype(algorithm, certificate):
    """
    Create a test pool by given categories.
    """
    click.echo('Creating a pool...')
    click.echo('Algorithm to pick up systems: %s' % algorithm)
    click.echo('Filter - Certify status : %s' % certificate)



@click.command()
@click.option('--location',
              type=click.Choice(['taipei', 'beijing', 'lexington', 'all']),
              default='taipei',
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
@click.option('--csv',
              default=True,
              help='If to output csv file with name'
              'location-certificate-enablement-status.csv')
def create(location, certificate, enablement, status, csv):
    """
    Create a test pool by given categories.
    """
    cids_objs = cids.get_cids(location, certificate, enablement, status)
    csv_fn = location + '-' + certificate + '-' + enablement + '-' + status
    csv_fn = csv_fn.replace(' ', '')
    csv_fn = csv_fn + '.csv'
    if csv:
        c3csv.generate_csv(cids_objs, csv_fn)
