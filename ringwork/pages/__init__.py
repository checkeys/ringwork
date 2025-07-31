import rio

from ringwork.components.navbar import Navbar
from ringwork.components.user import Restrict


@rio.page(name="Home", url_segment="", guard=Restrict)
class HomePage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            Navbar(),
            rio.PageView(grow_y=True)
        )


class MainPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(rio.PageView(grow_y=True))
