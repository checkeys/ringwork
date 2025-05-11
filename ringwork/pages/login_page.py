# coding:utf-8

from typing import List
from typing import Optional

from rio import Banner
from rio import Button
from rio import Card
from rio import Column
from rio import Component
from rio import Spacer
from rio import Text
from rio import TextInput
from rio import TextInputConfirmEvent
from rio import page
from rio_xpw.access import AccessControl
from rio_xpw.access import EndUser


@page(name="Login", url_segment="login")
class LoginPage(Component):
    """Login page for accessing the website."""

    # These are used to store the currently entered values from the user
    username: str = ""
    password: str = ""

    def __post_init__(self) -> None:
        self.__currently_logging_in: bool = False
        # self.__popup_open: bool = False
        self.__banner_text: str = ""

    async def _goto_public(self) -> None:
        self.session.navigate_to("/public")

    async def _login(self, _: Optional[TextInputConfirmEvent] = None) -> None:
        """Handles the login process when the user submits their credentials.

        It will check if the user exists and if the password is correct. If the
        user exists and the password is correct, the user will be logged in and
        redirected to the home page.
        """
        try:
            # Inform the user that something is happening
            self.__currently_logging_in = True
            self.force_refresh()

            #  Try to find a user with this name
            access_control: AccessControl = self.session[AccessControl]
            session_id: str = (enduser := self.session[EndUser]).session_id
            if not (user := access_control.activate(self.username, self.password, session_id)):  # noqa:E501
                self.__banner_text = "Please try again."
                return

            enduser.secret_key = user.secret_key
            self.session.attach(enduser)

            # The login was successful
            self.__banner_text = ""

            # The user is logged in - no reason to stay here
            target_url = self.session.active_page_url.query.get("target", "/")
            self.session.navigate_to(target_url=target_url)

        # Done
        finally:
            self.__currently_logging_in = False

    # def on_open_popup(self) -> None:
    #     """Opens the sign-up popup when the user clicks the sign-up button"""
    #     self.__popup_open = True

    def build(self) -> Component:
        components: List[Component] = []
        components.append(Text("Login", style="heading1", justify="center"))
        # Show error message if there is one
        #
        # Banners automatically appear invisible if they don't have
        # anything to show, so there is no need for a check here.
        components.append(Banner(text=self.__banner_text, style="danger", margin_top=1))  # noqa:E501
        # Create the login form consisting of a username and password
        # input field, a login button and a sign up button
        components.append(
            TextInput(
                text=self.bind().username,
                label="Username",
                # the login function is called when the user presses enter
                on_confirm=self._login,
            )
        )
        components.append(
            TextInput(
                text=self.bind().password,
                label="Password",
                # Mark the password field as secret so the password is
                # hidden while typing
                is_secret=True,
                # the login function is called when the user presses enter
                on_confirm=self._login,
            )
        )
        components.append(Spacer(min_height=0.1))
        components.append(
            Button(
                content="Sign In",
                on_press=self._login,
                is_loading=self.__currently_logging_in,
            )
        )
        components.append(
            Button(
                style="minor",
                on_press=self._goto_public,
                content="Access Public List",
            )
        )

        if self.session.window_width > 30.0:
            return Card(
                Column(*components, spacing=1.0, margin=2.0),
                min_width=24.0,
                margin_x=0.5,
                align_x=0.5,
                align_y=0.5,
            )
        else:
            return Card(
                Column(*components, spacing=1.0, margin=1.0),
                margin_x=2.0,
                align_y=0.5,
            )
