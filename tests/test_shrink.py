import c3.config as c3config
import pkg_resources
from c3.helper import compare, convert
from data.cids import cids_before_shrink, cids_after_shrink
from c3.shrink import shrink


configuration = c3config.Configuration.get_instance()

resource_package = __name__
path_test = '/'.join(('./data', 'test_conf.ini'))
ini_test = pkg_resources.resource_stream(resource_package, path_test)


def test_shrink_oem_18_04_pool():

    configuration.read_configuration(ini_test.name)

    cid_objs = convert.dict_to_cid_obj_cids(cids_before_shrink)
    cid_objs_shrank = shrink.get_pool(cid_objs)
    target = convert.cid_obj_to_dict_cids(cid_objs_shrank)

    assert len(cids_before_shrink) == 171
    assert len(cids_after_shrink) == 70
    assert compare.cid_objs(cids_after_shrink, target)


def test_sort_number():
    cid_objs = convert.dict_to_cid_obj_cids(cids_before_shrink)
    cid_objs_sorted = shrink.sort_cid_objs(cid_objs)

    assert len(cids_before_shrink) == len(cid_objs_sorted)
