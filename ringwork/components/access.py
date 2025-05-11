# coding:utf-8

from dataclasses import dataclass
from typing import Optional

from rio import App
from rio import GuardEvent
from rio import Session
from rio import UserSettings
from xpw import Account
from xpw import Profile
from xpw import Secret
from xpw import SessionID
from xpw import SessionUser


def Restrict(event: GuardEvent) -> Optional[str]:
    try:
        access_control: AccessControl = event.session[AccessControl]
        if profile := access_control.validate(user=event.session[EndUser]):
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

    def activate(self, username: str, password: str, session_id: str) -> Optional[SessionUser]:  # noqa:E501
        return self.accounts.login(username, password, session_id, Secret.generate().key)  # noqa:E501

    def deactivate(self, user: EndUser) -> bool:
        return self.accounts.logout(session_id=user.session_id, secret_key=user.secret_key)  # noqa:E501

    def validate(self, user: EndUser) -> Optional[Profile]:
        return self.accounts.fetch(session_id=user.session_id, secret_key=user.secret_key)  # noqa:E501

    async def on_app_start(self, app: App) -> None:
        app.default_attachments.append(self)

    async def on_session_start(self, rio_session: Session) -> None:
        if not (enduser := rio_session[EndUser]).session_id:
            enduser.session_id = SessionID.generate()
            rio_session.attach(enduser)
