import c3.maptable
from c3.pool.cid import CID


ma = c3.maptable.machine_metainfo_attr + c3.maptable.device_audio_attr


def dict_to_cid_obj_cids(cids):
    rtn_cids = []
    for cid in cids:
        cid_obj = CID(cid=cid)
        for attr_map in cids[cid]:
            cid_obj.__dict__.update(**attr_map)
        rtn_cids.append(cid_obj)

    return rtn_cids

def cid_obj_to_dict_cids(cids):
    rtn_cids = {}
    for cid in cids:
        cid_id = cid.cid
        rtn_cids[cid_id] = []
        for attr in ma:
            attr_element = {}
            attr_element[attr] = getattr(cid, attr)
            rtn_cids[cid_id].append(attr_element)

    return rtn_cids
