# coding:utf-8

from rio import Column
from rio import Component
from rio import PageView
from rio import Text
from rio import page

from ringwork.components.layout import NavbarLayout


@page(name="Overview", url_segment="")
class OverviewPage(Component):

    def build(self) -> Component:
        return NavbarLayout(
            content=Column(
                Text(text="Overview", style="heading2"),
                *[
                    # TODO
                ],
                spacing=1.0,
            ),
        )


class MainPage(Component):
    def build(self) -> Component:
        return Column(PageView(grow_y=True))
