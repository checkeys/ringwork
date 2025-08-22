import dataclasses
from typing import Optional

import rio
from xpw import Account


def Restrict(event: rio.GuardEvent) -> Optional[str]:
    try:
        account: Account = event.session[Account]
        setting: UserSettings = event.session[UserSettings]
        if profile := account.fetch(session_id=setting.session_id, secret_key=setting.secret_key):  # noqa:E501
            event.session.attach(profile)
            return
    except KeyError:
        pass

    return "/login"


@dataclasses.dataclass
class UserSettings(rio.UserSettings):
    """Model for data stored client-side for each user.

    Any classes inheriting from `rio.UserSettings` will be automatically
    stored on the client's device when attached to the session. Thus, we
    can check if the user has a valid auth token stored.

    This prevents users from having to log-in again each time the page is
    accessed.
    """

    session_id: str
    secret_key: str
