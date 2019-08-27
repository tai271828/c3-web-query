import click
import logging
import c3.api.cids as c3cids
import c3.api.query as c3query
import c3.io.csv as c3csv
import c3.maptable as c3maptable


logger = logging.getLogger('c3_web_query')


@click.command()
@click.option('--cid',
              help='single CID to query.')
@click.option('--cid-list',
              help='CID list to query. One CID one row.')
@click.option('--csv',
              default='cid-components.csv',
              help='Output file of your query result.')
@click.option('--certificate',
              type=click.Choice(['14.04.5', '16.04 LTS']),
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
def query(cid, cid_list, csv, certificate, enablement, status):
    """
    Query CID(s) status.

    This command is very useful when we want to know the EOL list etc.
    (See eol command below)

    :param cid: string, CID
    :param cid_list: a text file with CID string each row
    :param csv: the output file of query result
    :param certificate: query condition "certificate"
    :param enablement: query condition "enablement status"
    :param status: query condition, the certificate issue status
    :return: None
    """
    logger.info("Begin to execute.")

    cids = []

    if cid:
        cids.append(cid)

    if cid_list:
        cids_from_list = read_cids(cid_list)
        cids.extend(cids_from_list)

    cid_objs = c3cids.get_cids_by_query('all', certificate, enablement,
                                        status, cids)

    if csv:
        c3csv.generate_csv(cid_objs, csv)


@click.command()
@click.option('--holder',
              help='To be holder. Use Launchpad ID.')
@click.option('--location',
              type=click.Choice(['taipei', 'beijing', 'lexington', 'ceqa',
                                 'oem']),
              default='taipei',
              help='Change to location')
@click.option('--status',
              type=click.Choice(['return', 'canonical']),
              help='Change to status')
@click.option('--eol/--no-eol',
              default=False,
              help='Batch holder/location/status change to be '
                   'AsIs-OEM-Returned to partner/customer')
@click.option('--verbose/--no-verbose',
              default=False,
              help='Output the query result in simple format')
@click.option('--cid',
              help='single CID to query.')
@click.option('--cid-list',
              help='CID list to query. One CID one row.')
def location(holder, location, status, eol, verbose, cid, cid_list):
    """
    Update or query location information

    This command set will not only query C3 database but may also change
    some fields of the database according to your input parameters.

    :param holder: string, holder ID (same as Launchpad ID)
    :param location: string, map to location ID automatically
    :param status: string
    :param eol: equivalent to location "OEM" and status "Returned to partner/customer"
    :param verbose: verbose execution output
    :param cid: string, CID
    :param cid_list: a text file with CID string each row
    :return: None
    """
    logger.info("Begin to execute.")

    cids = []

    if cid:
        cids.append(cid)

    if cid_list:
        cids_from_list = read_cids(cid_list)
        cids.extend(cids_from_list)

    if holder and location:
        change_location_holder(cids, location, holder, status)
    elif eol:
        location = 'oem'
        status = 'return'
        change_location_holder(cids, location, holder, status)
    elif verbose:
        query_location_holder(cids, verbose=verbose)
    else:
        query_location_holder(cids)


def query_location_holder(cids, verbose=False):
    for cid_to_change in cids:
        ctc = cid_to_change
        holder_asis, location_asis, status_asis, platform_name = \
            c3query.query_holder_location(ctc)
        if verbose:
            print('====== CID %s ======' % ctc)
            print('Current location: %s' % location_asis)
            print('Current holder: %s' % holder_asis)
            print('Current status: %s' % status_asis)
            print('Current platform name: %s' % platform_name)
        else:
            print('{}, {}, {}, {}'.format(ctc, platform_name,
                                       location_asis, holder_asis))


def change_location_holder(cids, location, holder, status):
    for cid_to_change in cids:
        ctc = cid_to_change
        holder_asis, location_asis, status_asis, platform_name = \
            c3query.query_holder_location(ctc)
        print('============ CID %s ============' % ctc)
        print('Current location: %s' % location_asis)
        print('Current holder: %s' % holder_asis)
        print('Current status: %s' % status_asis)
        print('\nChanging holder and location...\n')
        if not holder:
            holder = holder_asis
        if not location:
            location = location_asis
        if not status:
            status = status_asis
        c3query.push_holder(ctc, holder)
        c3query.push_location(ctc, location)
        c3query.push_status(ctc, status)
        print('\nChanged.\n')
        holder_asis, location_asis, status_asis, platform_name = \
            c3query.query_holder_location(ctc)
        print('Current location: %s' % location_asis)
        print('Current holder: %s' % holder_asis)
        print('Current status: %s' % status_asis)


def read_cids(cid_list_file):
    rtn = []
    fhandler = open(cid_list_file, 'r')
    lines = fhandler.readlines()
    for line in lines:
        rtn.append(line.strip())

    return rtn


@click.command()
@click.option('--series',
              type=click.Choice(['trusty']),
              default='trusty',
              help='Which series including its point releases.')
@click.option('--office',
              type=click.Choice(['taipei-office', 'canonical']),
              default='taipei-office',
              help='Where the CID comes from.')
def eol(series, office):
    """
    Find out all EOL CIDs

    The algorithm to find out the EOL CIDs is based on the above query and
    location commands.

    For EOL we do the following steps:
        1. Query CIDs according to location with the "location command"
        2. According to the CIDs above to filter the certificate and
        enablement status

    :param certificate: series including their point releases
    :param location: location string
    :return: None
    """
    logger.info("Begin to execute.")

    releases = c3maptable.series['trusty']
    locations = c3maptable.office[office]

    cid_objs = []
    for release in releases:
        for location in locations:
            for enablement in ['Enabled', 'Certified']:
                for status in ['Complete - Pass', 'Revoked']:
                    logger.info('Fetching CIDs: {} {} {} {}'.format(release,
                                                                    location,
                                                                    enablement,
                                                                    status))
                    cid_obj = c3cids.get_cids(location,
                                              release,
                                              enablement,
                                              status,
                                              use_cache=False,
                                              filter_kernel=False)

                    cid_objs.extend(cid_obj)

    c3csv.generate_csv(cid_objs, 'EOL-CIDs.csv')