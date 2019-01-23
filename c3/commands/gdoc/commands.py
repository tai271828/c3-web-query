import click
import csv
import time
import logging
import c3.api.gdoc as c3gdoc
import c3.api.query as c3query


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
def google_doc(doc_type, doc_id,
               tab, cell, column, target_column,
               output):
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
        holder, location = c3query.query_holder_location(cid)
        target_data_c3.append([cid, holder, location])
        # in case the server rejects the high frequent query
        if sleep_counter % 100 == 0:
            time.sleep(1)

    logging.info("Output the result to {}".format(output))
    with open(output, 'w') as csv_file:
        fn = ['CID',
              'HOLDER - GDoc', 'HOLDER - C3',
              'Location - GDoc', 'Location - C3']
        writer = csv.DictWriter(csv_file, fieldnames=fn)
        writer.writeheader()
        for rn in range(len(target_data_sheet)):
            sheet_row = target_data_sheet[rn]
            c3_row = target_data_c3[rn]
            print('Dumping {}'.format(sheet_row[0]))
            writer.writerow({'CID': sheet_row[0],
                             'HOLDER - GDoc': sheet_row[1],
                             'HOLDER - C3': c3_row[1],
                             'Location - GDoc': sheet_row[2],
                             'Location - C3': c3_row[2]})
