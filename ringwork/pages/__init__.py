# coding:utf-8

from rio import Column
from rio import Component
from rio import PageView
from rio import page

from ringwork.components.access import Restrict
from ringwork.components.sshkey import SSHKeyComponent


@page(name="Home", url_segment="", guard=Restrict)
class HomePage(Component):
    def build(self) -> Component:
        return SSHKeyComponent()


class MainPage(Component):
    def build(self) -> Component:
        return Column(PageView(grow_y=True))
