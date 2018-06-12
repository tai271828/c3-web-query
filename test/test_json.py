import c3.json.component as c3component
import c3.config as c3config
import pkg_resources
from c3.helper import compare, convert
from data.machine import machine_report, machine_metainfo
from data.cids import cids_before_shrink, cids_after_shrink
from c3.shrink import shrink


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

def test_shrink():

    configuration.read_configuration(ini_test.name)

    cid_objs = convert.dict_to_cid_obj_cids(cids_before_shrink)
    cid_objs_shrank = shrink.get_pool(cid_objs)
    target = convert.cid_obj_to_dict_cids(cid_objs_shrank)

    assert compare.cid_objs(cids_after_shrink, target)
