from asyncio import Protocol
from aioapi.request import Request
from httptools import HttpRequestParser

from aioapi.http_parser import HttpParserMixin


class Server(Protocol, HttpParserMixin):
    def __init__(self, loop, handler, app):
        self._loop = loop
        self._encoding = "utf-8"
        self._app = app
        self._url = None
        self._headers = {}
        self._body = None
        self._transport = None
        self._request_parser = HttpRequestParser(self)
        self._request = None
        self._request_class = Request
        self._request_handler = handler
        self._request_handler_task = None

    def connection_made(self, transport):
        self._transport = transport

    def connection_lost(self, *args):
        self._transport = None

    def data_received(self, data):
        self._request_parser.feed_data(data)

    def response_writer(self, response):
        self._transport.write(str(response).encode(self._encoding))  # type: ignore
        self._transport.close()  # type: ignore
