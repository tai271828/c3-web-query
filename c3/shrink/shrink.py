import c3.config
import logging


logger = logging.getLogger('c3_web_query')


def sanity_check(base, target):
    for key in base:
        if key not in target:
            raise Exception

    if len(base) != len(target):
        raise Exception

def get_unique_devices_in_pool(cid_objs, category):
    devices_in_pool = []
    device_counts_in_pool = {}
    for cid_obj in cid_objs:
        device = getattr(cid_obj, category)
        if device not in devices_in_pool:
            devices_in_pool.append(device)
        if device in device_counts_in_pool.keys():
            device_counts_in_pool[device] += 1
        else:
            device_counts_in_pool[device] = 1

    sanity_check(devices_in_pool, device_counts_in_pool.keys())

    unique_devices_in_pool = []
    for device in device_counts_in_pool.keys():
        if device_counts_in_pool[device] == 1:
            unique_devices_in_pool.append(device)

    return unique_devices_in_pool

def get_pool(cid_objs):
    conf_singlet = c3.config.Configuration.get_instance()
    flag_all = conf_singlet.config['SHRINK'].getboolean('all')

    # Will try to find unique device in the pool
    device_categories = ['processor', 'video', 'wireless', 'network',
                         'audio_pciid', 'audio_name']

    # Check the configuration to see what shrink filter we are going to use.
    # Remove the filter not found in the configuration.
    if flag_all:
        logger.info('All filter are going to use.')
    else:
        logger.info('Begin to remove filters...')
        for category in device_categories:
            if conf_singlet.config['SHRINK'].getboolean(category) is None:
                device_categories.remove(category)
                logger.warning("No such category %s" % category)

    # Find unique devices per category
    category_unique_devices = {}
    for category in device_categories:
        unique_d_pool = get_unique_devices_in_pool(cid_objs, category)
        category_unique_devices[category] = unique_d_pool

    all_unique_devices = []
    for category in category_unique_devices.keys():
        all_unique_devices.extend(category_unique_devices[category])

    # Begin to shrink
    cid_objs_shrunk = []
    for category in device_categories:
        logging.debug("Shrink the pool by %s" % category)
        for cid_obj in cid_objs:
            device = getattr(cid_obj, category)
            if device in all_unique_devices:
                cid_objs_shrunk.append(cid_obj)

    print('Before shrink: %i CIDs in the pool' % len(cid_objs))
    print('After shrink:  %i CIDs in the pool' % len(cid_objs_shrunk))

    return cid_objs_shrunk
