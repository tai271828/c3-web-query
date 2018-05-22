import requests
import logging
from http.client import IncompleteRead


class QueryError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class APIQuery:

    def __init__(self, instance_uri, timeout=30.0, max_retries=10):
        self.instance_uri = instance_uri
        self.session = requests.session()
        self.timeout = timeout
        self.max_retries = max_retries

    def batch_query(self, *args, **kwargs):
        results = []
        kwargs['timeout'] = self.timeout
        next_query = None
        # Continue until a request entirely fails
        # or we don't get a request for another chunk
        while True:
            if next_query:
                args = (self.instance_uri + next_query,) + args[:-1]
            success = False
            for tries in range(self.max_retries):
                try:
                    if next_query:
                        # Using kwargs causes a bug with next_query
                        batch = self.session.get(*args)
                    else:
                        batch = self.session.get(*args, **kwargs)
                    if batch.ok:
                        # json is callable in requests >= 1.0
                        if callable(batch.json):
                            decoded_content = batch.json()
                        else:
                            decoded_content = batch.json
                        results.extend(decoded_content["objects"])
                        success = True
                        next_query = decoded_content['meta']['next']
                        break
                except (IncompleteRead,
                        ValueError,
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout) as excp:
                    logging.warning(excp)
            if not success:
                raise QueryError("Could not query {} succesfully "
                                 "after {} tries.".format(self.instance_uri,
                                                          self.max_retries))
            if not next_query:
                break
        return results

    def single_query(self, *args, **kwargs):
        kwargs['timeout'] = self.timeout
        for tries in range(self.max_retries):
            try:
                result = self.session.get(*args, **kwargs)
                if result.ok:
                    if callable(result.json):
                        decoded_content = result.json()
                    else:
                        decoded_content = result.json
                    return decoded_content
            except(IncompleteRead,
                   ValueError,
                   requests.exceptions.ConnectionError,
                   requests.exceptions.Timeout) as excp:
                logging.warning(excp)
        raise QueryError("Could not query {} succesfully "
                         "after {} tries.".format(self.instance_uri,
                                                  self.max_retries))
