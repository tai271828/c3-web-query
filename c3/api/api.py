"""
Global api singlet.
"""


class API(object):
    __instance = None

    def __init__(self):
        self.api = None
        self.request_params = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = API()
        return cls.__instance

    def set_api_params(self, api, params):
        self.api = api
        self.request_params = params
