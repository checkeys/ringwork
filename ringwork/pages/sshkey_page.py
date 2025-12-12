# coding:utf-8

from rio import Component
from rio import page

from ringwork.components.access import Restrict
from ringwork.components.layout import NavbarLayout
from ringwork.components.navbar import NavbarCommonButton
from ringwork.components.sshkey import ListComponent


@page(name="SSH Keys", url_segment="ssh", guard=Restrict)
class SSHKeyPage(Component):

    def build(self) -> Component:
        content = ListComponent()
        layout = NavbarLayout(content=content)
        layout.navbar.right.add(
            NavbarCommonButton(
                icon="material/upload",
                content="Upload",
                color="secondary",
                style="minor",
                on_press=content.upload_item,
            )
        )
        layout.navbar.right.add(
            NavbarCommonButton(
                icon="material/add",
                content="Create",
                color="success",
                style="minor",
                on_press=content.create_item,
            )
        )
        return layout
