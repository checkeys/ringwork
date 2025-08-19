import rio

from ringwork.components.navbar import Navbar
from ringwork.components.user import Restrict
from ringwork.pages.ssh_page import SSHPage


@rio.page(name="Home", url_segment="", guard=Restrict)
class HomePage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            Navbar(grow_y=False),
            SSHPage(grow_y=True),
        )


class MainPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(rio.PageView(grow_y=True))
