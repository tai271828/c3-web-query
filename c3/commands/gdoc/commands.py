import click
import c3.api.gdoc as c3gdoc
import c3.io.csv as c3csv


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
              default=True,
              help='If to output csv file with name '
              'diffrence.csv')
def google_doc(doc_type, doc_id,
               tab, cell, column, target_column,
               output):
    """
    CRUD of the google doc.
    """
    sheet = c3gdoc.get_sheet_data(doc_type, doc_id, tab, cell, column,
                                  target_column)
    print(sheet)


