# coding:utf-8

from fastapi.responses import PlainTextResponse


def _get_public_key(uid: str, kid: str) -> PlainTextResponse:
    return PlainTextResponse(content=f"uid: {uid}\nkid: {kid}")


async def get_public_key(uid: str, kid: str) -> PlainTextResponse:
    return _get_public_key(uid=uid, kid=kid)


async def download_public_key(uid: str, kid: str) -> PlainTextResponse:
    response = _get_public_key(uid=uid, kid=kid)
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = f"attachment; filename={kid}.pub"
    return response


async def get_public_list(pid: str) -> PlainTextResponse:
    return PlainTextResponse(content=f"pid: {pid}")
