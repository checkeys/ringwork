import rio

from ringwork.components.navbar import Navbar


class RootComponent(rio.Component):

    def build(self) -> rio.Component:
        return rio.Column(
            # The navbar contains a `rio.Overlay`, so it will always be on top
            # of all other components.
            Navbar(min_height=10.0),
            # The page view will display the content of the current page.
            rio.PageView(
                # Make sure the page view takes up all available space. Without
                # this the navbar would be assigned the same space as the page
                # content.
                grow_y=True,
            ),
        )


@rio.page(name="Home", url_segment="")
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
