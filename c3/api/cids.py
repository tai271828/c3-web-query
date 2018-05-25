"""
Providing CIDs according to different requests

Get ['CID', 'Release', 'Level', 'Location', 'Vendor'] list by
querying certificates in Taipei Cert lab.
"""
import os
import c3.config
import pickle
import logging
import pandas as pd
import c3.io.cache as c3cache
import c3.api.query as c3q
import c3.api.api as c3api
import c3.pool.cid as c3cid
from c3.api.api_utils import QueryError


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


def is_certified(summary, release, level, status):
    if summary['release']['release'] == release and \
       summary['level'] == level and \
       summary['status'] == status:
        return True
    else:
        return False


def get_cids_by_query(location, certificate, enablement, status, cids):
    try:
        print('Begin to query... ')
        summaries_taipei = get_certificates_by_location('taipei')
        # summaries_ceqa = get_certificates_by_location('ceqa')
        # summaries_beijin = get_certificates_by_location('beijing')
        summaries = summaries_taipei
        print('Get certificate-location result per CIDs')
        for summary in summaries:
            if is_certified(summary, certificate, enablement, status):
                cid_id = summary['machine'].split('/')[-2]
                print(cid_id)
                if summary['report'] is None:
                    logging.warning('This certificate has no submission.')
                else:
                    submission_id = summary['report'].split('/')[-2]
                    # TODO: use query_specific_submission instead
                    # submission_report = c3q.query_submission(submission_id)
                    cid_obj = c3cid.get_cid_from_submission(submission_id)
                    cid_obj.__dict__.update(cid=cid_id)
                    cids.append(cid_obj)
                    #generate_csv(summary, CSV_FILE)
    except QueryError:
        print("Problem with C3 Query")

    return cids


def get_cids(location, certificate, enablement, status):
    global request_params, api
    api = api_instance.api
    request_params = api_instance.request_params

    # Use cache is possible
    cids_cache = c3cache.read_cache("cids")
    if cids_cache:
        print("Found cids cache. Use it.")
        cids = cids_cache
    else:
        cids = []
        cids = get_cids_by_query(location, certificate, enablement, status,
                                 cids)
        c3cache.write_cache("cids", cids)

    return cids
