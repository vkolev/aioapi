import asyncio
import signal
from functools import partial

from aioapi import Server
from aioapi.exceptions import HTTPException
from aioapi.helpers import format_exception
from aioapi.response import Response
from aioapi.url_dispatch import UrlDispatcher


class Aioapi:
    def __init__(self, loop=None, middlewares=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        self._loop = loop
        self._router = UrlDispatcher()
        self._on_startup = []
        self._on_shutdown = []

        if middlewares is None:
            middlewares = []
        self._middlewares = middlewares

    @property
    def loop(self):
        return self._loop

    @property
    def router(self):
        return self._router

    @property
    def on_startup(self):
        return self._on_startup

    async def startup(self):
        coros = [func(self) for func in self._on_startup]
        await asyncio.gather(*coros, loop=self._loop)  # type: ignore

    async def shutdown(self):
        print("Shutdown process...")
        corors = [func(self) for func in self._on_shutdown]
        await asyncio.gather(*corors, loop=self._loop)  # type: ignore

    def add_route(self, method, path, handler):
        self._router.add_route(path, {method: handler})

    def _make_server(self):
        return Server(loop=self._loop, handler=self._handler, app=self)

    async def _handler(self, request, response_writer):
        """Process incomming requests"""
        try:
            match_info, handler = self._router.resolve(request)
            request.match_info = match_info
            if self._middlewares:
                for md in self._middlewares:
                    handler = partial(md, handler=handler)
            resp = await handler(request)
        except HTTPException as ex:
            resp = ex
        except Exception as ex:
            resp = format_exception(ex)

        if not isinstance(resp, Response):
            raise RuntimeError(f"expected Response instance, but got {type(resp)}")

        response_writer(resp)


def run_app(app, host="127.0.01", port=9090, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    protocol = app._make_server()
    loop.run_until_complete(app.startup())

    server = loop.run_until_complete(
        loop.create_server(lambda: protocol, host=host, port=port)
    )

    loop.add_signal_handler(
        signal.SIGTERM, lambda: asyncio.ensure_future(app.shutdown())
    )

    try:
        print(f"Started server on {host}:{port}")
        loop.run_until_complete(server.serve_forever())
    except KeyboardInterrupt:
        loop.run_until_complete(app.shutdown())
        server.close()
        loop.stop()
