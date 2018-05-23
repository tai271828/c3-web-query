"""
All api real query action will be collected here.
"""
import c3.config
import c3.api.api as c3api

configuration = c3.config.Configuration.get_instance()
api_instance = c3api.API.get_instance()


def query_location_vendor(cid):
    """
    Get hardware location and vendor's name by CID

    :param cid: string
    :return: string, string.
    """
    conf_instance = c3.config.Configuration.get_instance()
    c3url = conf_instance.config['C3']['URI']
    hardware_api = conf_instance.config['API']['hardware']
    result = api_instance.api.single_query(c3url + hardware_api + cid,
                                           params=api_instance.request_params)

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

    return get_machine_info(machine_report)


def get_machine_info(machine_report):
    """
    Get machine info

    :param machine_report: input of query_latest_machine_report, a dictionary
    :return: a dictionary to fill the report list
    """
    rtn_dict = {}
    keys = ['form_factor', 'make', 'model']

    # If there is no submission, machine_report is None
    if machine_report is None:
        for key in keys:
            rtn_dict[key] = "NA"
    else:
        for key in keys:
            rtn_dict[key] = machine_report.get(key, "NA")

    return rtn_dict


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
    lookup_table = {'beijing': '6', 'ceqa': '12', 'taipei': '13'}
    location = location.lower()
    api_location = api_location + lookup_table[location]

    return api_location
