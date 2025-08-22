import rio

from ringwork.components.keys import SSHKeyComponent
from ringwork.components.user import Restrict


@rio.page(name="Home", url_segment="", guard=Restrict)
class HomePage(rio.Component):
    def build(self) -> rio.Component:
        return SSHKeyComponent()


class MainPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(rio.PageView(grow_y=True))
