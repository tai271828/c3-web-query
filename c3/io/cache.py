"""
Handle cache io.
"""
import logging
import os
import pickle


def read_cache(prefix):
    pickle_fn = prefix + '.pickle'

    logging.info("Trying to find cache: %s" % pickle_fn)

    try:
        with open(pickle_fn, 'rb') as handle:
            cache_path = os.path.realpath(handle.name)
            logging.info('Found cache. Use cache as {}'.format(cache_path))
            result = pickle.load(handle)

    except FileNotFoundError:
        logging.warning('Cache not found.')
        result = None

    return result

def write_cache(prefix, result):
    pickle_fn = prefix + '.pickle'

    logging.info("Writing cache to file: %s" % pickle_fn)

    with open(pickle_fn, 'wb') as handle:
        cache_path = os.path.realpath(handle.name)
        pickle.dump(result, handle)
        logging.info('Saved cache at %s' % cache_path)

