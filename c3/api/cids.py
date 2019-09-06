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
import collections
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


# TODO: oh my god I did not use this function at all in this project?!
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



def get_certificates_by_location(location='Taipei', use_cache=True):
    """
    Get certificate information and the associated information by location api.

    :param location: string, e.g. Taipei
    :return: results
    """
    pickle_fn = location.lower() + '.cert_by_location.pickle'

    if configuration.config['GENERAL']['cache'] and use_cache:
        logger.info('Trying to find cache to get certificates by location.')

        try:
            with open(pickle_fn, 'rb') as handle:
                cache_path = os.path.realpath(handle.name)
                logger.info('Found cache. Use cache as {}'.format(cache_path))
                results = pickle.load(handle)
        except FileNotFoundError:
            logger.info('Cache not found. Fallback to web query.')
            results = c3q.query_certificates_by_location(location)

            with open(pickle_fn, 'wb') as handle:
                cache_path = os.path.realpath(handle.name)
                logger.info('Save cache at {}'.format(cache_path))
                pickle.dump(results, handle)

    else:
        results = c3q.query_certificates_by_location(location)

        if configuration.config['GENERAL']['cache'] and use_cache:
            with open(pickle_fn, 'wb') as handle:
                cache_path = os.path.realpath(handle.name)
                logger.info('Save cache at {}'.format(cache_path))
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


def has_same_len(base, target):
    if len(base) == len(target):
        return True
    else:
        return False


def get_cids_by_query(location, certificate, enablement, status,
                      target_cids=[], disable_flag=True,
                      use_cache=False,
                      filter_kernel=False):
    """
    Get cid objects by c3 query.

    :param location: location string
    :param certificate: certification distro
    :param enablement: enablement status
    :param status: certification status
    :param target_cids: mutually exculsive option of disable_flag
    :param disable_flag: mutually exculsive option of target_cids
    :param use_cache: if read and write pickle files
    :param filter_kernel: if enable the filter by kernel
    :return: cid objects in a list
    """
    # return cid objects
    cids = []
    try:
        print('Begin to query... ')
        summaries_location = []
        if location == 'all':
            summaries_not_merge = []
            # lcts: locations
            summaries_not_merge_lcts = []
            for location_entry in c3.maptable.location:
                summaries_entry = get_certificates_by_location(location_entry,
                                                               use_cache=use_cache)
                summaries_not_merge.append(summaries_entry)

                entry_locations = [location_entry] * len(summaries_entry)
                summaries_not_merge_lcts.append(entry_locations)

            summaries = merge_summaries(summaries_not_merge)
            summaries_location = merge_summaries(summaries_not_merge_lcts)

            if not has_same_len(summaries, summaries_location):
                logger.critical("Location flag list length is incorrect.")
                raise Exception

        else:
            summaries = get_certificates_by_location(location,
                                                     use_cache=use_cache)
            summaries_location = ['location']*len(summaries)

        logger.debug('Get certificate-location result per CIDs')
        counter_location = 0
        for summary in summaries:
            if is_certified(summary, certificate, enablement, status):
                cid_id = summary['machine'].split('/')[-2]

                if summary['report'] is None:
                    logger.warning('This certificate has no submission.')
                else:
                    if cid_id in target_cids or disable_flag:
                        print("Fetching data for {}".format(cid_id))

                        submission_id = summary['report'].split('/')[-2]
                        # TODO: use query_specific_submission instead
                        # submission_report = c3q.query_submission(submission_id)
                        cid_obj = c3cid.get_cid_from_submission(submission_id)
                        cid_obj.__dict__.update(cid=cid_id)
                        location_index = summaries.index(summary)
                        cid_location = summaries_location[location_index]
                        cid_obj.__dict__.update(location=cid_location)

                        if filter_kernel:
                            logging.info('Enable kernel version filter')
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
                        else:
                            cids.append(cid_obj)

            counter_location += 1

    except QueryError:
        logger.critical("Problem with C3 Query")

    return cids


def sanity_check(cid_objs):
    # TODO: This is a very bad way to sanity check the data
    # because it will drop the raw data
    #
    # make sure there is no duplicate entry
    cid_ids = []
    cid_objs_sorted = []
    for cid_obj in cid_objs:
        cid_ids.append(cid_obj.cid)

    duplicate_cids = []
    unique_cids = []
    for item, count in collections.Counter(cid_ids).items():
        if count > 1:
            duplicate_cids.append(item)
        else:
            unique_cids.append(item)

    cid_objs_duplicate_only = []
    for dcid in duplicate_cids:
        for cid_obj in cid_objs:
            if cid_obj.cid == dcid:
                cid_objs_duplicate_only.append(cid_obj)
                break

    cid_objs_unique_only = []
    for ucid in unique_cids:
        for cid_obj in cid_objs:
            if cid_obj.cid == ucid:
                cid_objs_unique_only.append(cid_obj)

    cid_objs_unique_cid = []
    cid_objs_unique_cid.extend(cid_objs_unique_only)
    if cid_objs_duplicate_only:
        cid_objs_unique_cid.extend(cid_objs_duplicate_only)
    cid_objs = cid_objs_unique_cid

    return cid_objs


def get_cids(location, certificate, enablement, status,
             cache_prefix='cids',
             target_cids=[], disable_flag=True,
             use_cache=False,
             filter_kernel=False):
    global request_params, api
    api = api_instance.api
    request_params = api_instance.request_params

    verbose_level = configuration.config['GENERAL']['verbose']
    c3config.set_logger_verbose_level(verbose_level, logger)

    logger.debug('logger begins to debug')

    cids_cache = []
    # Use cache is possible
    if use_cache:
        cids_cache = c3cache.read_cache(cache_prefix)

    if cids_cache:
        print("Found cids cache. Use it.")
        cids = cids_cache
    else:
        cids = get_cids_by_query(location, certificate, enablement, status,
                                 target_cids=target_cids,
                                 disable_flag=disable_flag,
                                 use_cache=use_cache,
                                 filter_kernel=filter_kernel)
        if use_cache:
            c3cache.write_cache("cids", cids)

    return cids
