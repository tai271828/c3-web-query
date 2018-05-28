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
import c3.maptable
import c3.config as c3config
import c3.io.cache as c3cache
import c3.api.query as c3q
import c3.api.api as c3api
import c3.pool.cid as c3cid
from c3.api.api_utils import QueryError


logger = logging.getLogger('c3_web_query')

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


def merge_summaries(summaries_not_merge):
    rtn_summaries = []
    for summaries in summaries_not_merge:
        rtn_summaries.extend(summaries)

    return rtn_summaries


def is_kernel_match_filter(filter_keywords, kernel_str):
    if filter_keywords is None:
        return False

    flag_all_in = True
    for key in filter_keywords:
        if key not in kernel_str:
            flag_all_in = False

    return flag_all_in


def get_cids_by_query(location, certificate, enablement, status, cids):
    try:
        print('Begin to query... ')
        if location == 'all':
            summaries_not_merge = []
            for location_entry in c3.maptable.location:
                summaries_entry = get_certificates_by_location(location_entry)
                summaries_not_merge.append(summaries_entry)
            summaries = merge_summaries(summaries_not_merge)

        else:
            summaries = get_certificates_by_location(location)

        print('Get certificate-location result per CIDs')
        for summary in summaries:
            if is_certified(summary, certificate, enablement, status):
                cid_id = summary['machine'].split('/')[-2]
                print(cid_id)

                if summary['report'] is None:
                    logger.warning('This certificate has no submission.')
                else:
                    submission_id = summary['report'].split('/')[-2]
                    # TODO: use query_specific_submission instead
                    # submission_report = c3q.query_submission(submission_id)
                    cid_obj = c3cid.get_cid_from_submission(submission_id)
                    cid_obj.__dict__.update(cid=cid_id)

                    # TODO: a workaround to filter kernel criteria
                    try:
                        filter_kernel = \
                            configuration.config['FILTER']['kernel']
                    except KeyError:
                        filter_kernel = ''

                    filter_keywords = filter_kernel.split('-')
                    if filter_kernel and \
                       is_kernel_match_filter(filter_keywords, cid_obj.kernel):
                        cids.append(cid_obj)
                    elif filter_kernel:
                        logger.warning('Skip as a workaround.')
                    else:
                        cids.append(cid_obj)

    except QueryError:
        print("Problem with C3 Query")

    return cids


def get_cids(location, certificate, enablement, status):
    global request_params, api
    api = api_instance.api
    request_params = api_instance.request_params

    verbose_level = configuration.config['GENERAL']['verbose']
    c3config.set_logger_verbose_level(verbose_level, logger)

    logger.debug('logger begins to debug')

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
