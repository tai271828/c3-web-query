"""
Providing CIDs according to different requests

Get ['CID', 'Release', 'Level', 'Location', 'Vendor'] list by
querying certificates in Taipei Cert lab.
"""
import os
import csv
import c3.config
import pickle
import pandas as pd
from c3.api.api_utils import APIQuery, QueryError

CSV_FILE = 'cid-certification-vendor.csv'
FIELDNAMES = ['CID', 'Release', 'Level', 'Form Factor', 'Manufacturer',
              'Model', 'Location', 'Vendor']

api = None
request_params = None
configuration = c3.config.Configuration.get_instance()


def query_location_vendor(cid):
    """
    Get hardware location and vendor's name by CID

    :param cid: string
    :return: string, string.
    """
    conf_instance = c3.config.Configuration.get_instance()
    c3url = conf_instance.config['C3']['URI']
    hardware_api = conf_instance.config['API']['hardware']
    result = api.single_query(c3url + hardware_api + cid,
                              params=request_params)

    if result['location']:
        info_location = result['location'].get('name', 'NA')
    else:
        info_location = 'NA'

    info_vendor = 'NA'
    if result['platform']:
        if result['platform']['vendor']:
            info_vendor = result['platform']['vendor'].get('name', 'NA')
    else:
        info_vendor = 'NA'

    return info_location, info_vendor


def get_cid_from_cert_lot_result(result):
    """
    Get CID from a certificate-by-location query result.

    The query looks like:
        '[hardware_api]/201404-14986/'

    This function is a parser to get 201404-14986.

    :param result: elements of results queried from C3 certificate API
    :return: string, CID
    """
    return result['machine'].split('/')[-2]


def query_latest_machine_report(cid):
    """
    Get machine report (from factor etc.) by CID

    :param cid: CID, string
    :return:
    """
    c3username = configuration.config['C3']['UserName']
    c3apikey = configuration.config['C3']['APIKey']
    c3url = configuration.config['C3']['URI']
    report_api = c3.config.Configuration.get_instance().config['API'][
        'reportFind']
    req_params = {"username": c3username,
                  "api_key": c3apikey,
                  "canonical_id": cid,
                  "limit": "1",
                  "order_by": "-created_at"}

    report = api.single_query(c3url + report_api, params=req_params)

    if len(report['objects']) == 0:
        machine_report = None
    else:
        machine_report = report['objects'][0]

    return get_machine_info(machine_report)


def get_machine_info(machine_report):
    """
    Get machine info

    :param machine_report: input of query_latest_machine_report, a dictionary
    :return: a dictionary to fill the report list
    """
    rtn_dict = {}
    keys = ['form_factor', 'make', 'model']

    # If there is no submission, machine_report is None
    if machine_report is None:
        for key in keys:
            rtn_dict[key] = "NA"
    else:
        for key in keys:
            rtn_dict[key] = machine_report.get(key, "NA")

    return rtn_dict


def generate_csv(result, csv_file):
    """
    Generate CSV with CID-Location-Release-Level information.

    The csv will looks like:
        CID Release Level
        201404-14986, 12.04 LTS, Certified Pre-install

    :param result: result queried
    :param csv_file: output csvfile
    :return: None
    """
    cid = get_cid_from_cert_lot_result(result)
    print("Getting info for {}…".format(cid))
    info_location, info_vendor = query_location_vendor(cid)

    with open(csv_file, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        if result:
            machine_info = query_latest_machine_report(cid)

            print("Updating csv file with data for {}…".format(cid))
            # They are maybe None
            if result['release']:
                info_release = result['release'].get('release', 'NA')
            else:
                info_release = 'NA'
            if result['level']:
                info_level = result['level']
            else:
                info_level = 'NA'
            writer.writerow({'CID': cid,
                             'Release': info_release,
                             'Level': info_level,
                             'Form Factor': machine_info['form_factor'],
                             'Manufacturer': machine_info['make'],
                             'Model': machine_info['model'],
                             'Location': info_location,
                             'Vendor': info_vendor
                             })
        else:
            print("No data for {}".format(cid))
            writer.writerow({'CID': cid,
                             'Release': ""})


def get_location_api_by_location(location='Taipei'):
    """
    Get location api by location name.

    :param location: string, e.g. Taipei
    :return: str, location api
    """
    api_location = configuration.config['API']['location']

    # Please note the number 13 means Taipei Cert lab and
    # it changes when the data structure of C3 changes.
    # It could be the other number. Please use the API doc
    # to get the number you expected.
    lookup_table = {'taipei': '13'}
    location = location.lower()
    api_location = api_location + lookup_table[location]

    return api_location


def query_certificates_by_location(location='Taipei'):
    print("Get certificates by the specified location: %s" % location)
    print('This will take around 3 minutes. Please be patient...')

    c3url = configuration.config['C3']['URI']
    api_location = get_location_api_by_location(location)

    results = api.batch_query(c3url + api_location, params=request_params)

    return results


def get_certificates_by_location(location='Taipei'):
    """
    Get certificate information and the associated information by location api.

    :param location: string, e.g. Taipei
    :return: results
    """
    pickle_fn = 'cert_by_location.pickle'

    if configuration.config['GENERAL']['cache']:
        print('Trying to find cache to get certificates by location.')

        try:
            with open(pickle_fn, 'rb') as handle:
                cache_path = os.path.realpath(handle.name)
                print('Found cache. Use cache as {}'.format(cache_path))
                results = pickle.load(handle)
        except FileNotFoundError:
            print('Cache not found. Fallback to web query.')
            results = query_certificates_by_location(location)

            with open(pickle_fn, 'wb') as handle:
                cache_path = os.path.realpath(handle.name)
                print('Save cache at {}'.format(cache_path))
                pickle.dump(results, handle)

    else:
        results = query_certificates_by_location(location)

        with open(pickle_fn, 'wb') as handle:
            cache_path = os.path.realpath(handle.name)
            print('Save cache at {}'.format(cache_path))
            pickle.dump(results, handle)

    return results


def go():
    global request_params, api
    c3url = configuration.config['C3']['URI']
    c3username = configuration.config['C3']['UserName']
    c3apikey = configuration.config['C3']['APIKey']
    api = APIQuery(c3url)

    request_params = {"username": c3username,
                      "api_key": c3apikey}

    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()

    try:
        print('Begin to query... ')
        results = get_certificates_by_location('taipei')
        print('Get certificate-location result per CIDs')
        for result in results:
            generate_csv(result, CSV_FILE)
    except QueryError:
        print("Problem with C3 Query")
