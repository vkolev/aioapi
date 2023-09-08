import json

from yarl import URL


class Request:
    _encoding = "utf-8"

    def __init__(self, method, url, headers, version=None, body=None, app=None):
        self.version = version
        self._method = method.decode(self._encoding)
        self._url = URL(url.decode(self._encoding))
        self._headers = headers
        self._body = body
        self._app = app
        self._match_info = {}
        self._query_params = {}
        self._raw_url = url

    @property
    def method(self):
        return self._method

    @property
    def url(self):
        return self._url

    @property
    def headers(self):
        return self._headers

    @property
    def app(self):
        return self._app

    @property
    def query_params(self):
        return self._query_params

    @query_params.setter
    def query_params(self, query_params=None):
        url = self._url
        result = {}
        try:
            split_url = url.raw_query_string.split("?")[1]
            result = {
                x[0]: x[1] for x in [x.split("=") for x in split_url[1:].split("&")]
            }
        except Exception:
            self.query_params = result
        self._query_params = result

    @property
    def match_info(self):
        return self._match_info

    @match_info.setter
    def match_info(self, match_info):
        self._match_info = match_info

    def text(self):
        if self._body is not None:
            return self._body.decode(self._encoding)

    def json(self):
        text = self.text()
        if text is not None:
            return json.loads(text)

    def __repr__(self):
        return f"<Request at 0x{id(self)}"
