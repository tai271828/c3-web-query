"""
Pool entry data model. It's a CID most of the time.
"""
import c3.json.meta as c3meta
import c3.json.component as c3component
import c3.api.query as c3query


class CID(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_cid_from_submission(submission_report):
    cid = CID()
    #cid = c3meta.get_basic_metadata(submission_report, cid)
    #cid = c3component.get_basic_components(submission_report, cid)
    submission_id = submission_report['resource_uri'].split('/')[-2]
    machine_report = c3query.query_specific_machine_report(submission_id)

    return cid
