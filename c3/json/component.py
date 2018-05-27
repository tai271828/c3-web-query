"""
Convert C3 response in json to basic target information.
"""
import logging
from c3.maptable import machine_metainfo_attr as mma
from c3.maptable import device_audio_attr as daa


logger = logging.getLogger('c3_web_query')


def get_audio_component(device_report):
    rtn_device = {daa[0]: 'Unknown pciid',
                  daa[1]: 'Audio is not found'}

    for device in device_report:
        if device['bus'] == 'pci':
            try:
                if device['category']['name'] == 'AUDIO':
                    rtn_device[daa[0]] = device['identifier']
                    rtn_device[daa[1]] = device['name']
                    return rtn_device
            except Exception as e:
                logger.warning(e)

    return rtn_device


def get_machine_info(machine_report):
    """
    Get machine info

    :param machine_report: input of query_latest_machine_report, a dictionary
    :return: a dictionary to fill the report list
    """
    rtn_dict = {}
    keys = mma

    # If there is no submission, machine_report is None
    if machine_report is None:
        for key in keys:
            rtn_dict[key] = "NA"
    else:
        for key in keys:
            rtn_dict[key] = machine_report.get(key, "NA")

    return rtn_dict
