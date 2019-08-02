import os
import c3.config as c3config
import c3.api.query as c3query
import c3.json.component as c3component
import pkg_resources
from c3.api.api_utils import APIQuery
from data.machine import machine_report, machine_metainfo


configuration = c3config.Configuration.get_instance()

resource_package = __name__
path_test = '/'.join(('./data', 'test_conf.ini'))
ini_test = pkg_resources.resource_stream(resource_package, path_test)


def compare_shallow_dict(base, target):

    shared_items = set(base.items()) & set(target.items())

    return len(machine_metainfo) == len(shared_items) == len(target)

def test_query():
    # this test needs c3 database connection

    configuration.read_configuration(ini_test.name)

    api = APIQuery(configuration.config['C3']['URI'])

    rparam = {"username": os.environ.get('C3USERNAME', 'ubuntu'),
              "api_key": os.environ.get('C3APIKEY', 'ubuntu')}

    c3query.api_instance.set_api_params(api, rparam)

    machine_report_c3 = c3query.query_specific_machine_report(106445)

    mm = c3component.get_machine_info(machine_report_c3)

    assert compare_shallow_dict(machine_metainfo, mm)
