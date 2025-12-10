# coding:utf-8

from typing import Optional

from rio import Column
from rio import Component
from rio import GuardEvent
from rio import Text
from rio import page

from ringwork.components.layout import NavbarLayout


def Restrict(event: GuardEvent) -> Optional[str]:
    pass


@page(name="SSH Public List", url_segment="public", guard=Restrict)
class PublicListPage(Component):

    def build(self) -> Component:
        return NavbarLayout(
            # navbar=Navbar(
            #     children=[
            #         Button(
            #             content="Create",
            #             icon="material/add",
            #             color="success",
            #             shape="rounded",
            #             style="minor",
            #             on_press=self._on_press_create_item,
            #         ),
            #     ]
            # ),
            content=Column(
                Text(text="Public List", style="heading2"),
                # Banner(self.banner_text, style=self.banner_style),
                *[
                    # TODO
                ],
                spacing=1.0,
            ),
        )
