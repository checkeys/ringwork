import rio
from xpw import Account

from ringwork.components.user import UserSettings


class Navbar(rio.Component):
    """A navbar with a fixed position and responsive width."""

    # Make sure the navbar will be rebuilt when the app navigates to a different
    # page. While Rio automatically detects state changes and rebuilds
    # components as needed, navigating to other pages is not considered a state
    # change, since it's not stored in the component.
    #
    # Instead, we can use Rio's `on_page_change` event to trigger a rebuild of
    # the navbar when the page changes.
    @rio.event.on_page_change
    def on_page_change(self) -> None:
        # Rio comes with a function specifically for this. Whenever Rio is
        # unable to detect a change automatically, use this function to force a
        # refresh.
        self.force_refresh()

    async def on_logout(self) -> None:
        account: Account = self.session[Account]
        setting: UserSettings = self.session[UserSettings]
        account.logout(setting.session_id, setting.secret_key)
        self.session.navigate_to("/")

    def build(self) -> rio.Component:
        # Determine the layout based on the window width
        desktop_layout = self.session.window_width > 30

        try:
            # Which page is currently active? This will be used to highlight the
            # correct navigation button.
            #
            # `active_page_instances` contains `rio.ComponentPage` instances
            # that that are created during app creation. Since multiple pages
            # can be active at a time (e.g. /foo/bar/baz), this is a list rather
            # than just a single page.
            active_page = self.session.active_page_instances[1]
            active_page_url_segment = active_page.url_segment
        except IndexError:
            # Handle the case where there are no active sub-pages. e.g. when the
            # user is not logged in.
            active_page_url_segment = None

        # Create the content of the navbar. First we create a row with a certain
        # spacing and margin.  We can use the `.add()` method to add components
        # by condition to the row.
        navbar_content = rio.Row(spacing=1, margin=1)

        # Links can be used to navigate to other pages and
        # external URLs. You can pass either a simple string, or
        # another component as their content.
        navbar_content.add(
            rio.Link(
                rio.IconButton(
                    icon="material/home:fill",
                    style="plain-text",
                    min_size=2.5,
                ),
                "/",
            )
        )

        # This spacer will take up any superfluous space,
        # effectively pushing the subsequent buttons to the
        # right.
        navbar_content.add(rio.Spacer())

        # By sticking buttons into a `rio.Link`, we can easily
        # make the buttons navigate to other pages, without
        # having to write an event handler. Notice how there is
        # no Python function called when the button is clicked.
        navbar_content.add(
            rio.Link(
                rio.Button(
                    content="SSH",
                    icon="material/key",
                    style=(
                        "major"
                        if active_page_url_segment == "ssh"
                        else "plain-text"
                    ),
                ),
                target_url="/ssh",
            )
        )

        # Logout
        navbar_content.add(
            rio.Button(
                content="Logout",
                icon="material/logout",
                style="plain-text",
                on_press=self.on_logout,
            )
        )

        # Use a rectangle for visual separation
        return rio.Rectangle(
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
