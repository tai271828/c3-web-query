import c3.json.component as c3component
import c3.config as c3config
import pkg_resources
from data.machine import machine_report, machine_metainfo


configuration = c3config.Configuration.get_instance()

resource_package = __name__
path_test = '/'.join(('./data', 'test_conf.ini'))
ini_test = pkg_resources.resource_stream(resource_package, path_test)


def compare_shallow_dict(base, target):

    shared_items = set(base.items()) & set(target.items())

    return len(machine_metainfo) == len(shared_items) == len(target)

def test_get_machine_info():

    mm = c3component.get_machine_info(machine_report)

    assert compare_shallow_dict(machine_metainfo, mm)
