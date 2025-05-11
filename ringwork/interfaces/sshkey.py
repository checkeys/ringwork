# coding:utf-8

from fastapi import Request
from fastapi.responses import Response


async def public_key_get(request: Request) -> Response:
    return Response(
        content=f"{request.url.path}",
        media_type="text/plain",
    )
