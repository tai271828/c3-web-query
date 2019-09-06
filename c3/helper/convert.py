import c3.maptable
from c3.pool.cid import CID


ma = c3.maptable.machine_metainfo_attr + c3.maptable.device_audio_attr


def dict_to_cid_obj_cids(cids):
    rtn_cids = []
    for cid in cids:
        cid_obj = CID(cid=cid)
        for attr_map_key in cids[cid]:
            attr_map = {attr_map_key: cids[cid][attr_map_key]}
            cid_obj.__dict__.update(**attr_map)
        rtn_cids.append(cid_obj)

    return rtn_cids

def cid_obj_to_dict_cids(cids):
    rtn_cids = {}
    for cid in cids:
        cid_id = cid.cid
        rtn_cids[cid_id] = {}
        for attr in ma:
            rtn_cids[cid_id][attr] = getattr(cid, attr)

    return rtn_cids
