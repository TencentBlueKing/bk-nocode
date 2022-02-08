# -*- coding: utf-8 -*-
import logging

from .exceptions import APIException
from .utils import render_string

logger = logging.getLogger(__name__)


class RequestAPI(object):
    """Single request api"""

    HTTP_STATUS_OK = 200

    def __init__(self, client, method, host=None, path=None, description=""):
        self.host = host
        self.path = path
        self.client = client
        self.method = method

    def __call__(self, *args, **kwargs):
        try:
            return self._call(*args, **kwargs)
        except APIException as e:
            # Combine log message
            log_message = [
                e.error_message,
            ]
            log_message.append("url=%s" % e.url)
            if e.resp:
                log_message.append("content=%s" % e.resp.text)

            logger.exception("\n".join(log_message))

            # Try return error message from remote service
            if e.resp is not None:
                try:
                    return e.resp.json()
                except Exception:
                    pass
            return {"result": False, "message": e.error_message, "data": None}

    def _call(self, params=None, path_params=None):
        if self.method in ["GET", "HEAD"]:
            params, data = params, None
        elif self.method in ["POST", "PUT", "PATCH", "DELETE"]:
            params, data = None, params

        path = render_string(self.path, path_params) if path_params else self.path
        # Request remote server
        url = "%s/%s%s" % (self.host.rstrip("/"), self.client.stage, path)
        try:
            resp = self.client.request(self.method, url, params=params, data=data)
        except Exception as e:
            logger.exception(
                "Error occurred when requesting method=%s, url=%s", self.method, url
            )
            raise APIException(u"API调用出错, Exception: %s" % str(e), url=url)

        # Parse result
        if resp.status_code != self.HTTP_STATUS_OK:
            message = u"请求出现错误，请求HTTP状态码：%s" % resp.status_code
            raise APIException(message, resp=resp, url=url)

        # Response format json or text
        try:
            return resp.json()
        except Exception:
            raise APIException(u"返回数据格式不正确，统一为json", resp=resp, url=url)
