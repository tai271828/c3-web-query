import pickle
import os.path
import logging
import c3.config
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


logger = logging.getLogger('c3_web_query')

configuration = c3.config.Configuration.get_instance()

# If modifying these scopes, delete the file token.picle.
# TODO: Do I really need so many SCOPES?
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive"]


def connect_sheet():
    token_location = configuration.config['GOOGLE']['token']
    credential_location = configuration.config['GOOGLE']['credential']

    creds = None
    if os.path.exists(token_location):
        with open(token_location, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credential_location, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(token_location, 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    return service


def get_sheet_data(doc_type, doc_id, tab, cell, column):
    sheet = None
    if doc_type == 'cid-request':
        sheet = get_sheet_data_cid_request(doc_id, tab, cell, column)
    return sheet


def get_sheet_data_cid_request(doc_id, tab, cell, column):
    service = connect_sheet()

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
    """
    Indicate different target columns for different sheets.

    :param sheet: string, the tab name.
    :param target_column: int-cid,int-location,int-holder,
    :return: a list with elements [cid, location, holder]
    """
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


def filter_by_c3oem(data_c3):
    data_c3_new = []
    for rn in range(len(data_c3)):
        c3_row = data_c3[rn]
        if c3_row[1] != "OEM":
            continue
        data_c3_new.append(c3_row)

    return data_c3_new


def filter_by_diff(data_sheet, data_c3):
    data_c3_new = []
    for rn_i in range(len(data_c3)):
        c3_row = data_c3[rn_i]
        for rn_j in range(len(data_sheet)):
            sheet_row = data_sheet[rn_j]
            if c3_row[1] == sheet_row[1] and c3_row[2] == sheet_row[2]:
                continue
        data_c3_new.append(c3_row)

    return data_c3_new


def dimension_sync(data_sheet, data_c3):
    data_sheet_new = []
    for rn_i in range(len(data_c3)):
        data_c3_row = data_c3[rn_i]
        for rn_j in range(len(data_sheet)):
            data_sheet_row = data_sheet[rn_j]
            if data_c3_row[0] == data_sheet_row[0]:
                data_sheet_new.append(data_sheet_row)

    return data_sheet_new


def delete_oem_row(doc_id, tab, row):
    service = connect_sheet()
    # result = service.spreadsheets().values().update(spreadsheetId=doc_id,
    #                                                 range=tab,
    #                                                 valueInputOption='RAW',)
    body = {
        "requests": [
            {
               "deleteDimension": {
                   "range": {
                       "sheetId": tab,
                       "dimension": "ROWS",
                       "startIndex": row,
                       "endIndex": row + 1
                   }
               }
            }
        ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=doc_id,
                                                 body=body)
    request.execute()
