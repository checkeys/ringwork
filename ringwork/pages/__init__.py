import rio

from ringwork.components.user import Restrict


@rio.page(name="Home", url_segment="", guard=Restrict)
class HomePage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Markdown(
                """
# Buzzwordz Inc.!

Unleashing synergistic paradigms for unprecedented excellence since the day
after yesterday.
            """,
                min_width=60,
                align_x=0.5,
            ),
        )


class MainPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(rio.PageView(grow_y=True))
