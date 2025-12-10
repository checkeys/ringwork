# coding:utf-8

from rio import Button
from rio import Component
from rio import page

from ringwork.components.access import Restrict
from ringwork.components.layout import NavbarLayout
from ringwork.components.sshkey import ListComponent


@page(name="SSH Keys", url_segment="ssh", guard=Restrict)
class SSHKeyPage(Component):

    def build(self) -> Component:
        content = ListComponent()
        layout = NavbarLayout(content=content)
        layout.navbar.right.add(
            Button(
                content="Upload",
                icon="material/upload",
                color="secondary",
                shape="rounded",
                style="minor",
                on_press=content.upload_item,
            )

        )
        layout.navbar.right.add(
            Button(
                content="Create",
                icon="material/add",
                color="success",
                shape="rounded",
                style="minor",
                on_press=content.create_item,
            )
        )
        return layout
