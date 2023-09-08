import logging

from aioapi.request import Request


logger = logging.getLogger(__name__)


async def log_middleware(request: Request, handler):
    logger.setLevel(logging.DEBUG)
    status = None
    response = await handler(request)
    status = response.status
    logger.info(f"{request.method.upper()} - '{request.url.path}' {status}")
    return response
