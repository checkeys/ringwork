# coding:utf-8

from typing import Optional
from urllib.parse import urlencode

from rio import GuardEvent
from rio_xpw.access import AccessControl


def Redirect(target_url: str = "/") -> str:
    return f"/login?{urlencode({'target': target_url})}"


def Restrict(event: GuardEvent) -> Optional[str]:
    if not (session := event.session)[AccessControl].validate(session):
        return Redirect(event.active_pages[0].url_segment)
