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
    logger.debug('Sanity check completed. %s looks good.' % category)

    unique_devices_in_pool = []
    duplicate_devices_in_pool = []
    for device in device_counts_in_pool.keys():
        if device_counts_in_pool[device] == 1:
            unique_devices_in_pool.append(device)
        else:
            duplicate_devices_in_pool.append(device)

    return unique_devices_in_pool, duplicate_devices_in_pool


def get_group_cpu_name(ifamily, category, device):
    """
    Abstract layer to group i3, i5, i7 families.

    :param ifamily: which series of cpu we want to group
    :param category: category to make sure the input is processor
    :param device: device to check
    :return: grouped device name
    """
    ifamily_series = c3.maptable.ifamily_series
    if ifamily and category == 'processor':
        for ifamily_type in ifamily_series:
            if ifamily_type in device.lower():
                device = ifamily_type

    return device


def get_location(cid_objs):
    """
    Select CID objects by location filter

    :param cid_objs:  cid objects
    :return: cid objects
    """
    conf_singlet = c3.config.Configuration.get_instance()
    filter_session = conf_singlet.config['FILTER']

    locations = []
    try:
        locations = filter_session['location'].split('-')
    except KeyError:
        logger.warning("No location filter is defined in configuration files.")

    cid_obj_locations = []
    for cid_obj in cid_objs:
        for location in locations:
            # TODO: implement to set location attribute of cid
            if location in cid_obj.location:
                cid_obj_locations.append(cid_obj)

    return cid_obj_locations


def get_heros(cid_objs):
    conf_singlet = c3.config.Configuration.get_instance()
    filter_session = conf_singlet.config['FILTER']

    heros = []
    try:
        heros = filter_session['heros'].split('-')
    except KeyError:
        logger.warning("No hero platform is defined in configuration files.")

    cid_obj_heros = []
    for cid_obj in cid_objs:
        for hero in heros:
            if hero in cid_obj.model:
                cid_obj_heros.append(cid_obj)

    return cid_obj_heros


def if_blacklist(cid_id):
    conf_singlet = c3.config.Configuration.get_instance()
    filter_session = conf_singlet.config['FILTER']

    black_cids = []
    try:
        black_cids = filter_session['blacklist'].split('_')
    except KeyError:
        logger.debug('No blacklist is defined in configuration files.')

    if cid_id in black_cids:
        return True
    else:
        return False


def if_replacement(cid_obj, device):
    conf_singlet = c3.config.Configuration.get_instance()
    filter_session = conf_singlet.config['FILTER']

    cid_device = []
    try:
        cid_device = filter_session['replacement'].split('_')
    except KeyError:
        logger.warning('No replacement is defined in configuration files.')

    replace_device = getattr(cid_obj, cid_device[1])
    if cid_obj.cid == cid_device[0] and device == replace_device:
        return True
    else:
        return False


def label_selection_category(cid_objs, c_unique_devices, c_duplicate_devices):
    # merge
    category_devices = {}
    for key_ud in c_unique_devices:
        ud = c_unique_devices[key_ud]
        dd = c_duplicate_devices[key_ud]
        category_devices[key_ud] = ud + dd

    for cid in cid_objs:
        unique_label = []
        for category in category_devices.keys():
            device = getattr(cid, category)
            if device in category_devices[category]:
                unique_label.append(category)
                cid.__dict__.update(unique_label=unique_label)
                category_devices[category].remove(device)

        if len(unique_label) == 0:
            logger.critical("Not found any unique device for cid %s" % cid.cid)
            return False

    return True


def sort_cid_objs(cid_objs):
    cid_ids = []
    cid_objs_sorted = []
    for cid_obj in cid_objs:
        cid_ids.append(cid_obj.cid)

    cid_ids.sort(reverse=True)

    for cid_id in cid_ids:
        for cid_obj in cid_objs:
            if cid_obj.cid == cid_id:
                cid_objs_sorted.append(cid_obj)

    return cid_objs_sorted


def shrink_by_category(cid_objs, device_categories, ifamily=False):
    """
    Shrinnk the pool by each category

    :param cid_objs: CID objects
    :param device_categories: which category to be referred when shrinking
    :param ifamily: how to group ifamily, e.g. i5-xxxx are all i5 family
    :return: shrunk CID objects
    """
    # sorting first to make sure each shrink result consistent
    cid_objs = sort_cid_objs(cid_objs)
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
    logger.debug("All unique devices: %s" % all_unique_devices)

    print('Before shrink: %i CIDs in the pool' % len(cid_objs))
    # Begin to shrink
    # phase 1: pick up those very unique
    cid_objs_shrunk = []
    # pick up heros first
    cid_obj_heros = get_heros(cid_objs)
    for cid_obj in cid_obj_heros:
        flag_pickup = False
        for category in device_categories:
            device = getattr(cid_obj, category)

            device = get_group_cpu_name(ifamily, category, device)

            if device in list(all_unique_devices):
                logger.debug('Select heros first by category %s' % category)
                if if_blacklist(cid_obj.cid) or if_replacement(cid_obj, device):
                    pass
                else:
                    flag_pickup = True
                    # then I don't need to pick up this device anymore in the
                    # latter steps
                    all_unique_devices.remove(device)

        if flag_pickup:
            cid_objs_shrunk.append(cid_obj)

    # pick up systems by location priority
    # if it is assigned in the location filter
    # it will be picked up earlier
    cid_obj_locations = get_location(cid_objs)
    for cid_obj in cid_obj_locations:
        flag_pickup = False
        for category in device_categories:
            device = getattr(cid_obj, category)

            device = get_group_cpu_name(ifamily, category, device)

            if device in list(all_unique_devices):
                if if_blacklist(cid_obj.cid) or if_replacement(cid_obj, device):
                    pass
                else:
                    logger.info('Select specific location first'
                                ' by category %s' % category)
                    flag_pickup = True
                    # then I don't need to pick up this device anymore in the
                    # latter steps
                    all_unique_devices.remove(device)

        if flag_pickup:
            cid_objs_shrunk.append(cid_obj)

    # after selecting hero platforms, now select common platforms
    for cid_obj in cid_objs:
        flag_pickup = False
        for category in device_categories:
            logging.debug("Shrink the pool by %s" % category)
            device = getattr(cid_obj, category)

            device = get_group_cpu_name(ifamily, category, device)

            if device in all_unique_devices:
                if if_blacklist(cid_obj.cid) or if_replacement(cid_obj, device):
                    pass
                else:
                    flag_pickup = True
                    # then I don't need to pick up this device anymore in the
                    # latter steps
                    all_unique_devices.remove(device)

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
                    if if_blacklist(cid_obj.cid) or if_replacement(cid_obj, device):
                        pass
                    else:
                        flag_pickup = True
                        all_duplicate_devices.remove(device)

        if flag_pickup:
            cid_objs_shrunk.append(cid_obj)

    # we have shrank the pool already. let's append the meta data to elaborate
    # the unique device category so users could know what is the reason to
    # select or not select this system.
    label_selection_category(cid_objs_shrunk,
                             category_unique_devices,
                             category_duplicate_devices)

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
        logger.debug('All filter are going to use.')
    else:
        logger.debug('Begin to remove filters...')
        for category in list(device_categories):
            # None or False, means we don't want to use the filter
            filter_flag = shrink_session.getboolean(category)
            if not filter_flag:
                device_categories.remove(category)
                logger.debug("Forbid to use category %s" % category)

    cid_objs_shrunk =  shrink_by_category(cid_objs,
                                          device_categories,
                                          filter_session.getboolean('ifamily'))

    return cid_objs_shrunk


def get_pool_not_select(cid_objs, cid_objs_shrank):
    cid_objs_rtn = []
    for cid_obj in cid_objs:
        flag = False
        for cid_obj_shrank in cid_objs_shrank:
            if cid_obj.cid == cid_obj_shrank.cid:
                flag = True
                break
        if not flag:
            cid_objs_rtn.append(cid_obj)

    return cid_objs_rtn
