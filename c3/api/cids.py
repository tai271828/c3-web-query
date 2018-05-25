"""
Providing CIDs according to different requests

Get ['CID', 'Release', 'Level', 'Location', 'Vendor'] list by
querying certificates in Taipei Cert lab.
"""
import os
import csv
import c3.config
import pickle
import logging
import pandas as pd
import c3.api.query as c3q
import c3.api.api as c3api
import c3.pool.cid as c3cid
from c3.api.api_utils import QueryError

CSV_FILE = 'cid-certification-vendor.csv'
FIELDNAMES = ['CID', 'Release', 'Level', 'Form Factor', 'Manufacturer',
              'Model', 'Location', 'Vendor']

configuration = c3.config.Configuration.get_instance()
api_instance = c3api.API.get_instance()


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
    info_location, info_vendor = c3q.query_location_vendor(cid)

    with open(csv_file, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        if result:
            machine_info = c3q.query_latest_machine_report(cid)

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


def get_certificates_by_location(location='Taipei'):
    """
    Get certificate information and the associated information by location api.

    :param location: string, e.g. Taipei
    :return: results
    """
    pickle_fn = location.lower() + '.cert_by_location.pickle'

    if configuration.config['GENERAL']['cache']:
        print('Trying to find cache to get certificates by location.')

        try:
            with open(pickle_fn, 'rb') as handle:
                cache_path = os.path.realpath(handle.name)
                print('Found cache. Use cache as {}'.format(cache_path))
                results = pickle.load(handle)
        except FileNotFoundError:
            print('Cache not found. Fallback to web query.')
            results = c3q.query_certificates_by_location(location)

            with open(pickle_fn, 'wb') as handle:
                cache_path = os.path.realpath(handle.name)
                print('Save cache at {}'.format(cache_path))
                pickle.dump(results, handle)

    else:
        results = c3q.query_certificates_by_location(location)

        with open(pickle_fn, 'wb') as handle:
            cache_path = os.path.realpath(handle.name)
            print('Save cache at {}'.format(cache_path))
            pickle.dump(results, handle)

    return results


def get_cid_component_by_submission(result):
    pass


def is_certified(summary, release, level, status):
    if summary['release']['release'] == release and \
       summary['level'] == level and \
       summary['status'] == status:
        return True
    else:
        return False


def go():
    global request_params, api
    api = api_instance.api
    request_params = api_instance.request_params

    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()

    try:
        print('Begin to query... ')
        summaries_taipei = get_certificates_by_location('taipei')
        summaries_ceqa = get_certificates_by_location('ceqa')
        summaries_beijin = get_certificates_by_location('beijing')
        summaries = summaries_taipei
        print('Get certificate-location result per CIDs')
        for summary in summaries:
            if is_certified(summary,
                            '16.04 LTS', 'Enabled', 'Complete - Pass'):
                cid_id = summary['machine'].split('/')[-2]
                print(cid_id)
                if summary['report'] is None:
                    logging.warning('This certificate has no submission.')
                else:
                    submission_id = summary['report'].split('/')[-2]
                    # TODO: use query_specific_submission instead
                    # submission_report = c3q.query_submission(submission_id)
                    c3cid.get_cid_from_submission(submission_id)
                    #generate_csv(summary, CSV_FILE)
    except QueryError:
        print("Problem with C3 Query")
