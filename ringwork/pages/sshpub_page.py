# coding:utf-8

from rio import Column
from rio import Component
from rio import Text
from rio import page

from ringwork.components.layout import NavbarLayout
from ringwork.components.navbar import NavbarCommonButton


@page(name="SSH Public List", url_segment="public")
class PublicListPage(Component):

    def build(self) -> Component:
        layout = NavbarLayout(content=Column(
            Text(text="Public List", style="heading2"),
            # Banner(self.banner_text, style=self.banner_style),
            *[
                # TODO
            ],
            spacing=1.0,
        ))
        layout.navbar.right.add(
            NavbarCommonButton(
                icon="material/add",
                content="Create",
                color="success",
                style="minor",
                # on_press=self._on_press_create_item,
            )
        )
        return layout
