#!/usr/bin/env python3
import os
import pickle
import pprint
import c3.maptable
import c3.config as c3config
from c3.shrink import shrink


def cid_obj_to_dict(cids):
    output = {}
    for cid in cids:
        cid_id = cid.cid
        output[cid_id] = []
        for attr in ma:
            attr_element = {}
            attr_element[attr] = getattr(cid, attr)
            output[cid_id].append(attr_element)

    return output

configuration = c3config.Configuration.get_instance()
configuration.read_configuration(os.environ['HOME'] +'/work/c3-web-query-working/my_conf.ini')


f = open('cids.pickle', 'rb')
cids = pickle.load(f)

ma = c3.maptable.machine_metainfo_attr + c3.maptable.device_audio_attr

output = cid_obj_to_dict(cids)
pprint.pprint(output)

cids_shrank = shrink.get_pool(cids)
output_shrank = cid_obj_to_dict(cids_shrank)

pprint.pprint('===========')
pprint.pprint(output_shrank)

