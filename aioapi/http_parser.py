class HttpParserMixin:
    def on_body(self, data):
        self._body = data

    def on_url(self, url):
        self._url = url

    def on_message_complete(self):
        self._request = self._request_class(  # type: ignore
            version=self._request_parser.get_http_version(),  # type: ignore
            method=self._request_parser.get_method(),  # type: ignore
            url=self._url,  # type: ignore
            headers=self._headers,  # type: ignore
            body=self._body,  # type: ignore
            app=self._app,  # type: ignore
        )  # type: ignore

        self._request_handler_task = self._loop.create_task(  # type: ignore
            self._request_handler(self._request, self.response_writer)  # type: ignore
        )

    def on_header(self, header, value):
        header = header.decode(self._encoding)  # type: ignore
        self._headers[header] = value.decode(self._encoding)  # type: ignore
