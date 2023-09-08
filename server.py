import logging
from aioapi.application import Aioapi, run_app
from aioapi.middlewares import log_middleware
from aioapi.response import Response


app = Aioapi(middlewares=[log_middleware])

logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG
)


async def handler(request):
    return Response(f"Hello at {request.url}")


async def hello_name(request):
    return Response(f"Hello {request.match_info['name']}")


app.add_route("GET", "/", handler)
app.add_route("GET", "/hello/:name", hello_name)

if __name__ == "__main__":
    run_app(app)
