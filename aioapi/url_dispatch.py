from aioapi.exceptions import HTTPMethodNotAllowed, HTTPNotFound
from aioapi.request import Request
from aioapi.response import Response
from aioapi.routing import Routes


class UrlDispatcher:
    def __init__(self):
        self._routes = Routes()

    async def _not_found(self, request):
        return Response(f"Not found {request.url} on this server", status=404)

    def add_route(self, path: str, methods_handler: dict):
        self._routes.add(path, methods_handler)

    def resolve(self, request: Request):
        try:
            match = self._routes.match(request.url.raw_path)
            parameters = match.params if match.params else {}
            handler = match.anything.get(request.method.upper())
            if not handler:
                raise HTTPMethodNotAllowed(
                    reason=f"{request.method.upper()} Not allowed for {request.url.raw_path}"
                )
            return parameters, handler
        except Exception:
            raise HTTPNotFound(reason=f"Could not find {request.url.raw_path}")
