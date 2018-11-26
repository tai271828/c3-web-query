import logging
import c3.config
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http


logger = logging.getLogger('c3_web_query')

configuration = c3.config.Configuration.get_instance()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive"]


def get_sheet_data(doc_type, doc_id, tab, cell, column):
    sheet = None
    if doc_type == 'cid-request':
        sheet = get_sheet_data_cid_request(doc_id, tab, cell, column)
    return sheet


def get_sheet_data_cid_request(doc_id, tab, cell, column):
    token = configuration.config['GOOGLE']['token']
    credential = configuration.config['GOOGLE']['credential']

    store = file.Storage(token)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(credential, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    # READING
    range_name = tab + '!' + cell + ':' + column
    result = service.spreadsheets().values().get(spreadsheetId=doc_id,
                                                 range=range_name).execute()

    values = result.get('values', [])

    if not values:
        logging.warning('No data found.')

    return values


def get_target_data(sheet, target_column):
    tc = target_column.split(',')
    rows = []
    if not sheet:
        print('No data found.')
    else:
        for row in sheet:
            row_target = []
            string_template = '{} ' * len(tc)
            for col in tc:
                col = int(col)
                # strip the string, e.g. cid
                # to make the process more robust
                row_target.append(row[col].strip())
            print(string_template.format(*row_target))
            rows.append(row_target)

    return rows
