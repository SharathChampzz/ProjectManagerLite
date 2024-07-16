from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import logging

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger("app")
        body = await request.body()
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request method: {request.method}")
        # logger.info(f"Request body: {body.decode('utf-8')}")
        response = await call_next(request)
        return response