# coding:utf-8

from typing import Optional

from rio import Component
from rio import GuardEvent
from rio import page

from ringwork.components.public import PubListComponent


def Restrict(event: GuardEvent) -> Optional[str]:
    pass


@page(name="Public List", url_segment="public", guard=Restrict)
class PublicPage(Component):

    def build(self) -> Component:
        return PubListComponent()
