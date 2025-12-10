# coding:utf-8

from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from xkeys_ssh import SSHKeyPair
from xkeys_ssh import SSHKeyRing
from xpw import Account
from xpw import Profile


class PublicKeyAPI:
    DOWNLOAD_PATH = "/api/ssh/pub/download/{uid}/{kid}"
    RAW_PATH = "/api/ssh/pub/raw/{uid}/{kid}"

    def __init__(self, accounts: Account):
        self.__accounts: Account = accounts

    @property
    def accounts(self) -> Account:
        return self.__accounts

    async def get(self, uid: str, kid: str) -> PlainTextResponse:
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

    async def download(self, uid: str, kid: str) -> PlainTextResponse:
        response = await self.get(uid=uid, kid=kid)
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Content-Disposition"] = f"attachment; filename={kid}.pub"  # noqa:E501
        return response
