import click
import logging
import c3.api.cids as c3cids
import c3.api.query as c3query
import c3.io.csv as c3csv


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
              type=click.Choice(['taipei', 'beijing', 'lexington', 'ceqa']),
              default='taipei',
              help='Change to location')
@click.option('--cid',
              help='single CID to query.')
@click.option('--cid-list',
              help='CID list to query. One CID one row.')
def location(holder, location, cid, cid_list):
    logger.info("Begin to execute.")

    cids = []

    if cid:
        cids.append(cid)

    if cid_list:
        cids_from_list = read_cids(cid_list)
        cids.extend(cids_from_list)

    for cid_to_change in cids:
        ctc = cid_to_change
        holder_asis, location_asis = c3query.query_holder_location(ctc)
        print('====== CID %s ======' % ctc)
        print('Current location: %s' % location_asis)
        print('Current holder: %s' % holder_asis)
        print('Changing holder and location...')
        c3query.push_holder(ctc, holder)
        c3query.push_location(ctc, location)
        print('Changed.\n')
        holder_asis, location_asis = c3query.query_holder_location(ctc)
        print('Current location: %s' % location_asis)
        print('Current holder: %s' % holder_asis)


def read_cids(cid_list_file):
    rtn = []
    fhandler = open(cid_list_file, 'r')
    lines = fhandler.readlines()
    for line in lines:
        rtn.append(line.strip())

    return rtn
