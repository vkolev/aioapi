import http.server
import json
from typing import Mapping

web_responses: Mapping[
    int, tuple[str, str]
] = http.server.BaseHTTPRequestHandler.responses


class Response:
    _encoding = "utf-8"

    def __init__(
        self,
        body=None,
        status=200,
        content_type="text/plain",
        headers=None,
        version="1.1",
    ):
        self._version = version
        self._status = status
        self._body = body
        self._content_type = content_type
        if headers is None:
            headers = {}
        self._headers = headers

    @property
    def body(self):
        return self._body

    @property
    def status(self):
        return self._status

    @property
    def content_type(self):
        return self._content_type

    @property
    def headers(self):
        return self._headers

    def add_body(self, data):
        self._body = data

    def add_header(self, key, value):
        self._headers[key] = value

    def __str__(self):
        """We use this to generate the raw HTTP Response that will be passed to TCP transport"""
        status_msg, _ = web_responses.get(self._status)  # type: ignore

        messages = [
            f"HTTP/{self._version} {self._status} {status_msg}",
            f"Content-Type: {self._content_type}",
            f"Conetnt-Length: {len(self.body)}",  # type: ignore
        ]

        if self.headers:
            for header, value in self.headers.items():
                messages.append(f"{header}: {value}")

        if self._body is not None:
            messages.append("\r\n" + self._body)

        return "\r\n".join(messages)

    def __repr__(self):
        return f"<Response 0x{id(self)}"


def make_error_response(error: str, status_code: int) -> Response:
    error_msg = {
        "error": [{"message": error}],
        "is_success": False,
        "status_code": status_code,
    }
    return Response(
        status=status_code,
        body=json.dumps(error_msg),
        content_type="application/json",
    )
