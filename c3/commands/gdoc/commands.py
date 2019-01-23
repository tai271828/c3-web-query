import click
import csv
import time
import logging
import c3.api.gdoc as c3gdoc
import c3.api.query as c3query
import c3.api.api_utils as c3api


@click.command()
@click.option('--doc-type',
              type=click.Choice(['cid-request', 'ceqa']),
              default='cid-request',
              help='Which type of the doc.')
@click.option('--doc-id',
              help='The doc unique ID.')
@click.option('--tab',
              help='The tab name of the doc.')
@click.option('--cell',
              help='The cell number in column-row format.')
@click.option('--column',
              help='The column number.')
@click.option('--target-column',
              default='0,1,7',
              help='The target column numbers, separated by commas.')
@click.option('--output',
              default='diffrence.csv',
              help='If to output csv file with name diffrence.csv')
@click.option('--output-filter',
              type=click.Choice(['all', 'C3OEM', 'diff']),
              default='all',
              help='Only output: C3OEM, location on C3 is OEM. Diff: '
                   'location or holder differs.')
@click.option('--delete-mode',
              type=click.Choice(['dry', 'delete']),
              help='If we want to delete the sheet entry when the C3 '
                   'location is OEM.')
@click.option('--delete-tab-id',
              default='0',
              help='When deleting tab, what is its sheetID.')
def google_doc(doc_type, doc_id,
               tab, cell, column, target_column,
               output, output_filter, delete_mode, delete_tab_id):
    """
    CRUD of the google doc.
    """
    sheet = c3gdoc.get_sheet_data(doc_type, doc_id, tab, cell, column)
    target_data_sheet = c3gdoc.get_target_data(sheet, target_column)
    print(target_data_sheet)

    cids = []
    for row in target_data_sheet:
        cid = row[0]
        cids.append(cid)

    target_data_c3 = []
    sleep_counter = 0
    for cid in cids:
        print('Fetching {} from c3'.format(cid))
        try:
            holder, location = c3query.query_holder_location(cid)
        except c3api.QueryError:
            logging.warning("Failed to query {}. Maybe no c3 data "
                            "entry.".format(cid))
            holder, location = "NA", "NA"
            print('TAI')

        target_data_c3.append([cid, location, holder])
        # in case the server rejects the high frequent query
        if sleep_counter % 100 == 0:
            time.sleep(1)

    if output_filter == 'C3OEM':
        target_data_c3 = c3gdoc.filter_by_c3oem(target_data_c3)
        target_data_sheet = c3gdoc.dimension_sync(target_data_sheet,
                                                  target_data_c3)
    elif output_filter == 'diff':
        target_data_c3 = c3gdoc.filter_by_diff(target_data_sheet,
                                               target_data_c3)
        target_data_sheet = c3gdoc.dimension_sync(target_data_sheet,
                                                  target_data_c3)
    elif output_filter == 'all':
        pass
    else:
        logging.error("No such mode.")

    logging.info("Output the result to {}".format(output))
    with open(output, 'w') as csv_file:
        fn = ['CID',
              'LOCATION - GDoc', 'LOCATION - C3',
              'HOLDER - GDoc', 'HOLDER - C3']
        writer = csv.DictWriter(csv_file, fieldnames=fn)
        writer.writeheader()
        for rn in range(len(target_data_sheet)):
            sheet_row = target_data_sheet[rn]
            c3_row = target_data_c3[rn]
            print('Dumping {}'.format(sheet_row[0]))
            writer.writerow({'CID': sheet_row[0],
                             'LOCATION - GDoc': sheet_row[1],
                             'LOCATION - C3': c3_row[1],
                             'HOLDER - GDoc': sheet_row[2],
                             'HOLDER - C3': c3_row[2]})

    if delete_mode == 'delete':
        c3gdoc.delete_oem_row(doc_id, delete_tab_id, 21)
