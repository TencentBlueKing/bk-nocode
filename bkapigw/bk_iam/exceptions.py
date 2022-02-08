# -*- coding: utf-8 -*-


class BaseException(Exception):
    pass


class APIException(BaseException):
    """Exception for API"""

    def __init__(self, error_message, resp=None, url=""):
        self.url = url
        self.error_message = error_message
        self.resp = resp

        if self.resp is not None:
            error_message = "%s, resp=%s" % (error_message, self.resp.text)
        super(APIException, self).__init__(error_message)
