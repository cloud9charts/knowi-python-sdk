class KnowiException(Exception):
    """Base class for client errors """
    pass


class KnowiApiException(KnowiException):
    """"""

    def __init__(self, rsp):
        self.rsp = rsp

    def __str__(self):
        return f'The Knowi API returned an error (status: {self.status}, message: {self.message})'

    @property
    def status(self):
        return self.rsp.status_code

    @property
    def message(self):
        try:
            return self.rsp.json()['message']
        except (ValueError, KeyError):
            return self.rsp.text