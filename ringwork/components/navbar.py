# coding:utf-8

from typing import Iterable
from typing import List

from rio import Button
from rio import Component
from rio import IconButton
from rio import Link
from rio import Rectangle
from rio import Row
from rio import Spacer
from rio import event
from xpw import Profile

from ringwork.components.access import AccessControl
from ringwork.components.access import EndUser


class Navbar(Component):
    """A navbar with a fixed position and responsive width."""

    left_children: Iterable[Component]
    right_children: Iterable[Component]

    @event.on_page_change
    def on_page_change(self) -> None:
        self.force_refresh()

    async def on_logout(self) -> None:
        access_control: AccessControl = self.session[AccessControl]
        if access_control.deactivate(user=self.session[EndUser]):
            self.session.navigate_to("/")

    async def on_login(self) -> None:
        self.session.navigate_to("/login")

    def build(self) -> Component:
        # Determine the layout based on the window width
        desktop_layout = self.session.window_width > 30

        # Create the content of the navbar.
        # First we create a row with a certain spacing and margin.
        # We can use the `.add()` method to add components by condition to
        # the row.

        left_content: List[Component] = [
            Link(
                content=IconButton(
                    icon="material/home:fill",
                    style="plain-text",
                    min_size=2.5,
                ),
                target_url="/",
            )
        ]

        access_control: AccessControl = self.session[AccessControl]
        if (profile := access_control.validate(user=self.session[EndUser])):
            left_content.append(
                Link(
                    content=IconButton(
                        icon="material/settings:fill",
                        style="plain-text",
                        min_size=2.5,
                    ),
                    target_url="/settings",
                )
            )

        for child in self.left_children:
            left_content.append(child)

        navbar_content = Row(
            *left_content,
            spacing=1.0,
            margin=1.0,
        )

        navbar_content.add(Spacer(grow_x=True))

        for child in self.right_children:
            navbar_content.add(child)

        if not isinstance(profile, Profile):
            # Login button
            navbar_content.add(
                Button(
                    content="Login",
                    icon="material/login",
                    shape="rounded",
                    color="secondary",
                    style="minor",
                    on_press=self.on_login,
                )
            )

        # Use a rectangle for visual separation
        return Rectangle(
            # Use the content we've built up by conditions
            content=navbar_content,
            # Set the fill of the rectangle to the neutral color of the theme
            fill=self.session.theme.neutral_color,
            # Round the corners
            corner_radius=self.session.theme.corner_radius_medium,
            # Add a shadow to make the navbar stand out above other content
            shadow_radius=0.8,
            shadow_color=self.session.theme.shadow_color,
            shadow_offset_y=0.2,
            # Overlay assigns the entire screen to its child component.
            # Since the navbar isn't supposed to take up all space, align
            # it.
            align_y=0,
            margin_x=2 if desktop_layout else 0.5,
            margin_y=2,
        )
