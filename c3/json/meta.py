"""
Convert C3 response in json to basic metadata information.
"""


class MetaInfo(object):

    def __init__(self, submission_report):
        self.sub_rpt = submission_report
        self.cid = None
        self.get_cid()

    def get_cid(self):
        # This also works but harder to read
        # self.cid = self.sub_rpt['hardware'].split('/')[-2]
        self.cid = self.sub_rpt['canonical_id']

    def dump(self, cid_obj):
        """
        Dump the meta data to the cid object

        :param cid_obj: cid object
        :return: None
        """
        pass


def get_basic_metadata(submission_report, cid_obj):
    """
    Get basic components

    :param submission_report: submission report in json
    :param cid: cid object
    :return: CID objects
    """
    metainfo = MetaInfo(submission_report)
    metainfo.dump(cid_obj)
