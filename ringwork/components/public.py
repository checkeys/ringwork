# coding:utf-8

from typing import Literal

from rio import Banner
from rio import Button
from rio import Column
from rio import Component
from rio import Text
from rio import event

from ringwork.components.navbar import Navbar


class PubListComponent(Component):
    """A CRUD page that allows users to create, read, update, and delete menu
    items.
    """

    banner_text: str = ""
    banner_style: Literal["success", "danger", "info"] = "success"

    @event.on_populate
    def on_populate(self) -> None:
        pass

    async def on_press_create_item(self) -> None:
        pass

    async def on_press_delete_item(self, name: str) -> None:
        pass

    def build(self) -> Component:
        """Builds the component to be rendered."""

        # Then unpack the list to pass the children to the ListView
        return Column(
            Navbar(
                left_children=[],
                right_children=[
                    Button(
                        content="Create",
                        icon="material/add",
                        color="success",
                        shape="rounded",
                        style="minor",
                        on_press=self.on_press_create_item,
                    ),
                ]
            ),
            Column(
                Text(text="Public List", style="heading2"),
                Banner(self.banner_text, style=self.banner_style),
                *[
                    # TODO
                ],
                # align at the top
                align_y=0.0,
                grow_y=True,
                spacing=1.0,
                margin_x=3.0,
            ),
        )
