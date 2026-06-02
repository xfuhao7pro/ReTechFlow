import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled API exception", exc_info=exc)
        return response

    detail = response.data
    message = detail.get("detail") if isinstance(detail, dict) else detail
    response.data = {
        "code": response.status_code,
        "msg": str(message or "请求处理失败"),
        "data": None,
        "errors": detail,
    }
    return response
