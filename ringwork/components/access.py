# coding:utf-8

from dataclasses import dataclass
from typing import Optional

from rio import App
from rio import GuardEvent
from rio import Session
from rio import UserSettings
from xpw import Account
from xpw import SessionID


def Restrict(event: GuardEvent) -> Optional[str]:
    try:
        account: Account = event.session[Account]
        enduser: EndUser = event.session[EndUser]
        if profile := account.fetch(session_id=enduser.session_id, secret_key=enduser.secret_key):  # noqa:E501
            event.session.attach(profile)
            return
    except KeyError:
        pass

    return "/public"


@dataclass
class EndUser(UserSettings):
    """Model for data stored client-side for each user.

    Any classes inheriting from `rio.UserSettings` will be automatically
    stored on the client's device when attached to the session. Thus, we
    can check if the user has a valid auth token stored.

    This prevents users from having to log-in again each time the page is
    accessed.
    """

    session_id: str
    secret_key: str


class AccessControl():
    NOBODY: EndUser = EndUser(session_id="", secret_key="")

    def __init__(self, accounts: Optional[Account] = None):
        self.__accounts: Account = accounts or Account.from_file()

    @property
    def accounts(self) -> Account:
        return self.__accounts

    async def on_app_start(self, app: App) -> None:
        app.default_attachments.append(self.accounts)

    async def on_session_start(self, rio_session: Session) -> None:
        enduser: EndUser = rio_session[EndUser]
        if not enduser.session_id:
            enduser.session_id = SessionID.generate()
            rio_session.attach(enduser)
