import click
import c3.api.cids as cids
import c3.io.csv as c3csv
from c3.shrink import shrink


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
              type=click.Choice(['14.04.5', '16.04 LTS', '18.04 LTS']),
              default='16.04 LTS',
              help='Filters to match certify status.')
@click.option('--enablement',
              type=click.Choice(['Enabled', 'Certified']),
              default='Enabled',
              help='Enabled(pre-installed), Certified(N+1).')
@click.option('--status',
              type=click.Choice(['Complete - Pass']),
              default='Complete - Pass',
              help='Certificate status')
@click.option('--csv-before-shrink',
              default=True,
              help='If true to output csv file with name'
              'location-certificate-enablement-status-before-shrink.csv')
@click.option('--csv-after-shrink',
              default=True,
              help='If true to output csv file with name'
              'location-certificate-enablement-status-after-shrink.csv')
@click.option('--csv-after-shrink-not-selected',
              default=True,
              help='If true to output csv file with name'
              'location-certificate-enablement-status-after-shrink-'
              'not-selected.csv')
def create(location, certificate, enablement, status,
           csv_before_shrink, csv_after_shrink, csv_after_shrink_not_selected):
    """
    Create a test pool by given categories.
    """
    cid_objs = cids.get_cids(location, certificate, enablement, status,
                             use_cache=True)

    cid_objs = cids.sanity_check(cid_objs)

    csv_fn = location + '-' + certificate + '-' + enablement + '-' + status
    csv_fn_prefix = csv_fn.replace(' ', '')
    csv_fn_output = csv_fn_prefix + '-before-shrink.csv'
    if csv_before_shrink:
        c3csv.generate_csv(cid_objs, csv_fn_output)

    cid_objs_shrank = shrink.get_pool(cid_objs)

    csv_fn_output_shrank = csv_fn_prefix + '-after-shrink.csv'

    if csv_after_shrink:
        c3csv.generate_csv(cid_objs_shrank, csv_fn_output_shrank)

    cid_objs_shrank_not_selected = shrink.get_pool_not_select(cid_objs,
                                                              cid_objs_shrank)
    suffix = '-after-shrink-not-selected.csv'
    csv_fn_output_shrank_not_selected = csv_fn_prefix + suffix

    if csv_after_shrink_not_selected:
        c3csv.generate_csv(cid_objs_shrank_not_selected,
                           csv_fn_output_shrank_not_selected)
