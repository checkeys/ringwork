# coding:utf-8

from typing import Optional

from rio import Component
from rio import GuardEvent
from rio import page
from xpw import Account

from ringwork.components.public import PubListComponent


def Restrict(event: GuardEvent) -> Optional[str]:
    account: Account = event.session[Account]
    # print(event.session.active_page_url.raw_parts)


@page(name="Public List", url_segment="public", guard=Restrict)
class PublicPage(Component):

    def build(self) -> Component:
        account: Account = self.session[Account]
        return PubListComponent()
