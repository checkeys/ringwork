from typing import List
from typing import Optional

import rio
from xpw import Account
from xpw import Secret

from ringwork.components.user import UserSettings


@rio.page(name="Login", url_segment="login")
class LoginPage(rio.Component):
    """Login page for accessing the website."""

    # These are used to store the currently entered values from the user
    username: str = ""
    password: str = ""

    error_message: str = ""
    popup_open: bool = False

    _currently_logging_in: bool = False

    async def login(self, _: Optional[rio.TextInputConfirmEvent] = None) -> None:  # noqa:E501
        """Handles the login process when the user submits their credentials.

        It will check if the user exists and if the password is correct. If the
        user exists and the password is correct, the user will be logged in and
        redirected to the home page.
        """
        try:
            # Inform the user that something is happening
            self._currently_logging_in = True
            self.force_refresh()

            #  Try to find a user with this name
            account: Account = self.session[Account]
            setting: UserSettings = self.session[UserSettings]
            user = account.login(self.username, self.password,
                                 session_id=setting.session_id,
                                 secret_key=Secret.generate().key)
            if not user:
                self.error_message = "Please try again."
                return

            setting.secret_key = user.secret_key
            self.session.attach(setting)

            # The login was successful
            self.error_message = ""

            # The user is logged in - no reason to stay here
            self.session.navigate_to(target_url="/")

        # Done
        finally:
            self._currently_logging_in = False

    def on_open_popup(self) -> None:
        """Opens the sign-up popup when the user clicks the sign-up button"""
        self.popup_open = True

    def build(self) -> rio.Component:
        # Determine the layout based on the window width
        desktop_layout = self.session.window_width > 30

        components: List[rio.Component] = []
        components.append(rio.Text("Login", style="heading1", justify="center"))  # noqa:E501
        # Show error message if there is one
        #
        # Banners automatically appear invisible if they don't have
        # anything to show, so there is no need for a check here.
        components.append(rio.Banner(text=self.error_message, style="danger", margin_top=1))  # noqa:E501
        # Create the login form consisting of a username and password
        # input field, a login button and a sign up button
        components.append(
            rio.TextInput(
                text=self.bind().username,
                label="Username",
                # the login function is called when the user presses enter
                on_confirm=self.login,
            )
        )
        components.append(
            rio.TextInput(
                text=self.bind().password,
                label="Password",
                # Mark the password field as secret so the password is
                # hidden while typing
                is_secret=True,
                # the login function is called when the user presses enter
                on_confirm=self.login,
            )
        )
        components.append(rio.Spacer(min_height=0.5))
        components.append(
            rio.Button(
                "Sign In",
                on_press=self.login,
                is_loading=self._currently_logging_in,
            )
        )

        return rio.Card(
            rio.Column(
                *components,
                spacing=1,
                margin=2 if desktop_layout else 1,
            ),
            margin_x=0.5,
            align_y=0.5,
            align_x=0.5 if desktop_layout else None,
            min_width=24 if desktop_layout else 0,
        )
