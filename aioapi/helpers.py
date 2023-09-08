import traceback
from aioapi.response import Response, make_error_response


server_exception = """
500 Internal Server Error
"""


def format_exception(exc: Exception) -> Response:
    trace = traceback.format_exc().replace("\n", "<br />")
    msg = server_exception.format(exc=str(exc), traceback=trace)
    return make_error_response(error=msg, status_code=500)
