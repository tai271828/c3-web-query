import logging
import c3.config
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


logger = logging.getLogger('c3_web_query')

configuration = c3.config.Configuration.get_instance()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive"]

def get_sheet_data(doc_type, doc_id, tab, cell, column, target_column):
    sheet = None
    if doc_type == 'cid-request':
        sheet = get_sheet_data_cid_request(doc_id, tab, cell, column,
                                           target_column)
    return sheet

def get_sheet_data_cid_request(doc_id, tab, cell, column, target_column):
    TOKEN = configuration.config['GOOGLE']['token']
    CREDENTIAL = configuration.config['GOOGLE']['credential']

    store = file.Storage(TOKEN)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CREDENTIAL, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    # READING
    RANGE_NAME = tab + '!' + cell + ':' + column
    result = service.spreadsheets().values().get(spreadsheetId=doc_id,
                                                range=RANGE_NAME).execute()

    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        cells = []
        for row in values:
            # Print target columns
            for col in target_column.split(','):
                col = int(col)
                cells.append(row[col])
            string_template = '{} ' * len(target_column.split(','))
            print(string_template.format(*cells))

    sheet = values
    return sheet
