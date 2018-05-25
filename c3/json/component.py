"""
Convert C3 response in json to basic target information.
"""
import logging


logger = logging.getLogger('c3_web_query')


def get_basic_components(submission_report):
    """
    Get basic components

    :param submission_report: submission report in json
    :return: CID objects
    """
    print(submission_report)
    pass


def get_components(device_report):
    print(device_report)
    pass


def get_audio_component(device_report):
    rtn_device = {'audio_pciid': 'Unknown pciid',
                  'audio_name': 'Audio is not found'}

    for device in device_report:
        if device['bus'] == 'pci':
            try:
                if device['category']['name'] == 'AUDIO':
                    rtn_device['audio_pciid'] = device['identifier']
                    rtn_device['audio_name'] = device['name']
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
    keys = ['make', 'model', 'codename', 'form_factor', 'processor',
            'video', 'wireless', 'network']

    # If there is no submission, machine_report is None
    if machine_report is None:
        for key in keys:
            rtn_dict[key] = "NA"
    else:
        for key in keys:
            rtn_dict[key] = machine_report.get(key, "NA")

    return rtn_dict
