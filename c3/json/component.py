"""
Convert C3 response in json to basic target information.
"""


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
    for device in device_report:
        if device['bus'] == 'pci':
            try:
                if device['category']['name'] == 'AUDIO':
                    return device['identifier'], device['name']
            except:
                pass
    return "Unknown pciid", "Audio is not found"
