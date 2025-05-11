# coding:utf-8

from rio import Column
from rio import Component

from ringwork.components.navbar import Navbar


class NavbarLayout(Component):

    content: Component

    def __post_init__(self) -> None:
        self.__navbar: Navbar = Navbar()

    @property
    def navbar(self) -> Navbar:
        return self.__navbar

    def build(self) -> Component:
        self.content.align_x = 0.0
        self.content.align_y = 0.0
        self.content.margin_x = 3.0
        self.content.margin_y = 0.0
        self.content.grow_x = True
        self.content.grow_y = True
        self.content.min_width = self.session.window_width - self.content.margin_x * 2  # noqa:E501

        return Column(self.navbar, self.content, grow_x=True, grow_y=True)
