"""
All api real query action will be collected here.
"""
import c3.config


configuration = c3.config.Configuration.get_instance()


def query_latest_machine_report(api, cid):
    """
    Get machine report (from factor etc.) by CID

    :param api: api object
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

    report = api.single_query(c3url + report_api, params=req_params)

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
