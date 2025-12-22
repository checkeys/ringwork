# coding:utf-8

from urllib.parse import urlencode

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.responses import PlainTextResponse
from xkeys_ssh import SSHKeyPair
from xkeys_ssh import SSHKeyRing
from xpw import Account
from xpw import Profile


class PublicKeyAPI:
    DOWNLOAD_PATH = "/api/ssh/pub/download"
    RAW_PATH = "/api/ssh/pub/raw"

    def __init__(self, accounts: Account):
        self.__accounts: Account = accounts

    @property
    def accounts(self) -> Account:
        return self.__accounts

    @classmethod
    def get_raw_url(cls, uid: str, kid: str) -> str:
        return f"{cls.RAW_PATH}?{urlencode({'uid': uid, 'kid': kid})}"

    @classmethod
    def get_download_url(cls, uid: str, kid: str) -> str:
        return f"{cls.DOWNLOAD_PATH}?{urlencode({'uid': uid, 'kid': kid})}"

    async def get(self, uid: str = Query(), kid: str = Query()) -> PlainTextResponse:  # noqa:E501
        profile: Profile = Profile(self.accounts, username=uid)
        keyring: SSHKeyRing = SSHKeyRing(base=profile.workspace)

        if kid not in keyring:
            raise HTTPException(status_code=404)

        try:
            keypair: SSHKeyPair = keyring[kid]
            public: str = keypair.public
        except Exception:
            raise HTTPException(status_code=500)

        return PlainTextResponse(content=public)

    async def download(self, uid: str = Query(), kid: str = Query()) -> PlainTextResponse:  # noqa:E501
        response = await self.get(uid=uid, kid=kid)
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Content-Disposition"] = f"attachment; filename={kid}.pub"  # noqa:E501
        return response
