import logging
import c3.config
from c3.maptable import comprehensive_cid_attr as cca


logger = logging.getLogger('c3_web_query')


def sanity_check(base, target):
    for key in base:
        if key not in target:
            logger.critical("Different device number.")
            raise Exception

    if len(base) != len(target):
        logger.critical("Different device number.")
        raise Exception

def get_unique_devices_in_pool(cid_objs, category, ifamily=False):
    ifamily_series = c3.maptable.ifamily_series
    devices_in_pool = []
    device_counts_in_pool = {}
    for cid_obj in cid_objs:
        device = getattr(cid_obj, category)

        # group i[3,5,7]-xxxx as i[3,5,7]
        device = get_group_cpu_name(ifamily, category, device)

        if device not in devices_in_pool:
            devices_in_pool.append(device)
        if device in device_counts_in_pool.keys():
            device_counts_in_pool[device] += 1
        else:
            device_counts_in_pool[device] = 1

    sanity_check(devices_in_pool, device_counts_in_pool.keys())
    logger.info('Sanity check completed. %s looks good.' % category)

    unique_devices_in_pool = []
    duplicate_devices_in_pool = []
    for device in device_counts_in_pool.keys():
        if device_counts_in_pool[device] == 1:
            unique_devices_in_pool.append(device)
        else:
            duplicate_devices_in_pool.append(device)

    return unique_devices_in_pool, duplicate_devices_in_pool


def get_group_cpu_name(ifamily, category, device):
    ifamily_series = c3.maptable.ifamily_series
    if ifamily and category == 'processor':
        for ifamily_type in ifamily_series:
            if ifamily_type in device.lower():
                device = ifamily_type

    return device


def shrink_by_category(cid_objs, device_categories, ifamily=False):
    # Find unique devices per category
    category_unique_devices = {}
    category_duplicate_devices = {}
    for category in device_categories:
        unique_d_pool, duplicate_d_pool = get_unique_devices_in_pool(
            cid_objs, category, ifamily)
        category_unique_devices[category] = unique_d_pool
        category_duplicate_devices[category] = duplicate_d_pool

    all_unique_devices = []
    all_duplicate_devices = []
    for category in category_unique_devices.keys():
        all_unique_devices.extend(category_unique_devices[category])
        all_duplicate_devices.extend(category_duplicate_devices[category])
    logger.info("All unique devices: %s" % all_unique_devices)

    print('Before shrink: %i CIDs in the pool' % len(cid_objs))
    # Begin to shrink
    # phase 1: pick up those very unique
    cid_objs_shrunk = []
    for cid_obj in cid_objs:
        flag_pickup = False
        for category in device_categories:
            logging.debug("Shrink the pool by %s" % category)
            device = getattr(cid_obj, category)

            device = get_group_cpu_name(ifamily, category, device)

            if device in all_unique_devices:
                flag_pickup = True

        if flag_pickup:
            cid_objs_shrunk.append(cid_obj)

    # phase 2: check which duplicate components were already picked up in
    # the systems with unique devices.
    for cid_obj in cid_objs_shrunk:
        for device in list(all_duplicate_devices):
            for category in device_categories:
                device_cid = getattr(cid_obj, category)
                device_cid = get_group_cpu_name(ifamily, category, device_cid)
                if device == device_cid:
                    all_duplicate_devices.remove(device)

    # phase 3: pick up systems based on the duplicate devices.
    # This phase is where we could set up the priority of location etc. when
    # picking up systems.
    for cid_obj in cid_objs_shrunk:
        cid_objs.remove(cid_obj)

    for cid_obj in cid_objs:
        flag_pickup = False
        for device in list(all_duplicate_devices):
            for category in device_categories:
                device_cid = getattr(cid_obj, category)
                device_cid = get_group_cpu_name(ifamily, category, device_cid)
                if device == device_cid:
                    all_duplicate_devices.remove(device)
                    flag_pickup = True

        if flag_pickup:
            cid_objs_shrunk.append(cid_obj)

    print('After shrink:  %i CIDs in the pool' % len(cid_objs_shrunk))

    return cid_objs_shrunk


def get_pool(cid_objs):
    conf_singlet = c3.config.Configuration.get_instance()
    shrink_session = conf_singlet.config['SHRINK']
    filter_session = conf_singlet.config['FILTER']
    flag_all = shrink_session.getboolean('all')

    # Will try to find unique device in the pool
    device_categories = cca

    # Check the configuration to see what shrink filter we are going to use.
    # Remove the filter not found in the configuration.
    if flag_all:
        logger.info('All filter are going to use.')
    else:
        logger.info('Begin to remove filters...')
        for category in list(device_categories):
            # None or False, means we don't want to use the filter
            filter_flag = shrink_session.getboolean(category)
            if not filter_flag:
                device_categories.remove(category)
                logger.warning("Forbid to use category %s" % category)

    cid_objs_shrunk =  shrink_by_category(cid_objs,
                                          device_categories,
                                          filter_session.getboolean('ifamily'))

    return cid_objs_shrunk
