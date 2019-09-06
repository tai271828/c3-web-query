"""
Pool entry data model. It's a CID most of the time.
"""
import c3.json.component as c3component
import c3.api.query as c3query
from pprint import pprint


class CID(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_cid_from_submission(submission_id):
    cid = CID()

    machine_report = c3query.query_specific_machine_report(submission_id)
    machine_metainfo = c3component.get_machine_info(machine_report)

    device_report = c3query.query_submission_devices(submission_id)
    device_audio = c3component.get_audio_component(device_report)

    cid.__dict__.update(**machine_metainfo)
    cid.__dict__.update(**device_audio)

    return cid


def dump_cid_obj(cid_obj):
    pprint(vars(cid_obj))
