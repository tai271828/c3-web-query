"""
All api real query action will be collected here.
"""
import c3.config
import c3.maptable
import c3.api.api as c3api
import requests
import logging

logger = logging.getLogger('c3_web_query')
format_str = "[ %(funcName)s() ] %(message)s"
logging.basicConfig(level=logging.INFO, format=format_str)

configuration = c3.config.Configuration.get_instance()
api_instance = c3api.API.get_instance()


def query_over_api_hardware(cid):
    conf_instance = c3.config.Configuration.get_instance()
    c3url = conf_instance.config['C3']['URI']
    hardware_api = conf_instance.config['API']['hardware']
    result = api_instance.api.single_query(c3url + hardware_api + cid,
                                           params=api_instance.request_params)

    return result


def query_location_vendor(cid):
    """
    Get hardware location and vendor's name by CID

    :param cid: string
    :return: string, string.
    """
    result = query_over_api_hardware(cid)

    if result['location']:
        info_location = result['location'].get('name', 'NA')
    else:
        info_location = 'NA'

    info_vendor = 'NA'
    if result['platform']:
        if result['platform']['vendor']:
            info_vendor = result['platform']['vendor'].get('name', 'NA')
    else:
        info_vendor = 'NA'

    return info_location, info_vendor


def query_certificates_by_location(location='Taipei'):
    print("Get certificates by the specified location: %s" % location)
    print('This will take around 3 minutes. Please be patient...')

    c3url = configuration.config['C3']['URI']
    api_location = get_location_api_by_location(location)

    results = api_instance.api.batch_query(c3url + api_location,
                                           params=api_instance.request_params)

    return results


def query_submission_devices(submission):
    """
    Return the device information by its submission ID.

    :param submission: submission ID
    :return: device report
    """
    c3url = configuration.config['C3']['URI']
    api_endpoint = configuration.config['API']['machineReport'] + \
                   submission + '/report_devices/'
    api_uri = c3url + api_endpoint
    # rp = api_instance.request_params
    # apiq = APIQuery(c3url)
    # machine_report = apiq.single_query(api_uri, params=rp)
    # TODO: not sure APIQuery does not work. Use request here instead.
    rp = {'username': configuration.config['C3']['UserName'],
          'api_key': configuration.config['C3']['APIKey'],
          'limit': configuration.config['C3']['BatchQueryMode']}

    response = requests.get(api_uri, params=rp)

    device_report = response.json()

    return device_report['objects']


def query_submission(submission_id):
    """
    Please use query_specific_machine_report instead.

    This function will timeout easily, before fixing this. Please use
    query_specific_machine_report instead.

    :param submission_id: submission_id, int represented in string
    :return: report in json
    """

    logger.info("Start querying")

    c3url = configuration.config['C3']['URI']
    api_endpoint = configuration.config['API']['machineReport'] + \
                   submission_id + '/'
    api_uri = c3url + api_endpoint

    rp = {'username': configuration.config['C3']['UserName'],
          'api_key': configuration.config['C3']['APIKey'],
          'limit': configuration.config['C3']['BatchQueryMode']}

    # TODO: timeout easily
    # response = requests.get(api_uri, params=rp)
    #
    # return response.json()
    report = api_instance.api.single_query(api_uri, timeout=60,
                                           params=rp)

    return report


def query_specific_machine_report(m_id):
    """
    Get machine report (from factor etc.) by machine report id

    :param m_id: submission / machine report id, string
    :return:
    """
    c3username = configuration.config['C3']['UserName']
    c3apikey = configuration.config['C3']['APIKey']
    c3url = configuration.config['C3']['URI']
    report_api = configuration.config['API']['reportFind']
    req_params = {"username": c3username,
                  "api_key": c3apikey,
                  "id": m_id}

    report = api_instance.api.single_query(c3url + report_api,
                                           params=req_params)

    if not len(report['objects']) == 1:
        print('Something wrong with the number.')
        return None

    if len(report['objects']) == 0:
        machine_report = None
    else:
        machine_report = report['objects'][0]

    return machine_report


def query_latest_machine_report(cid):
    """
    Get machine report (from factor etc.) by CID

    :param cid: CID, string
    :return:
    """
    c3username = configuration.config['C3']['UserName']
    c3apikey = configuration.config['C3']['APIKey']
    c3url = configuration.config['C3']['URI']
    report_api = configuration.config['API']['reportFind']
    req_params = {"username": c3username,
                  "api_key": c3apikey,
                  "canonical_id": cid,
                  "limit": "1",
                  "order_by": "-created_at"}

    report = api_instance.api.single_query(c3url + report_api,
                                           params=req_params)

    if len(report['objects']) == 0:
        machine_report = None
    else:
        machine_report = report['objects'][0]

    return machine_report


def get_location_api_by_location(location='Taipei'):
    """
    Get location api by location name.

    :param location: string, e.g. Taipei
    :return: str, location api
    """
    api_location = configuration.config['API']['location']

    # Please note the number 13 means Taipei Cert lab and
    # it changes when the data structure of C3 changes.
    # It could be the other number. Please use the API doc
    # to get the number you expected.
    #
    # 6: Beijing
    # 12: ce qa lab
    # 13: Taipei cert lab
    #
    lookup_table = c3.maptable.location
    location = location.lower()
    api_location = api_location + lookup_table[location]

    return api_location


def parse_holder(result):
    if result['holder']:
        info = result['holder'].get('display_name', 'NA')
    else:
        info = 'NA'

    return info


def parse_location(result):
    if result['location']:
        info_location = result['location'].get('name', 'NA')
    else:
        info_location = 'NA'

    return info_location


def query_holder_location(cid):
    result = query_over_api_hardware(cid)

    holder = parse_holder(result)
    location = parse_location(result)

    return holder, location


def push_holder(cid, holder):
    pass


def push_location(cid, location):
    pass
