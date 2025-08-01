from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pathlib import Path

import rio
from xpw import AuthInit
from xpw import TokenAuth

from ringwork.attribute import __description__
from ringwork.attribute import __project__
from ringwork.pages.home import HomePage


async def on_app_start(app: rio.App) -> None:
    auth: TokenAuth = AuthInit.from_file()
    app.default_attachments.append(auth)


async def on_session_start(rio_session: rio.Session) -> None:
    return

    # A new user has just connected. Check if they have a valid auth token.
    #
    # Any classes inheriting from `rio.UserSettings` will be automatically
    # stored on the client's device when attached to the session. Thus, by
    # retrieving the value here, we can check if the user has a valid auth token
    # stored.
    user_settings = rio_session[data_models.UserSettings]

    # Get the persistence instance
    pers = rio_session[persistence.Persistence]

    # Try to find a session with the given auth token
    try:
        user_session = await pers.get_session_by_auth_token(
            user_settings.auth_token,
        )

    # None was found - this auth token is invalid
    except KeyError:
        pass

    # A session was found. Welcome back!
    else:
        # Make sure the session is still valid
        if user_session.valid_until > datetime.now(tz=timezone.utc):
            # Attach the session. This way any component that wishes to access
            # information about the user can do so.
            rio_session.attach(user_session)

            # For a user to be considered logged in, a `UserInfo` also needs to
            # be attached.
            userinfo = await pers.get_user_by_id(user_session.user_id)
            rio_session.attach(userinfo)

            # Since this session has only just been used, let's extend its
            # duration. This way users don't get logged out as long as they keep
            # using the app.
            await pers.update_session_duration(
                user_session,
                new_valid_until=datetime.now(tz=timezone.utc)
                + timedelta(days=7),
            )


# Define a theme for Rio to use.
#
# You can modify the colors here to adapt the appearance of your app or website.
# The most important parameters are listed, but more are available! You can find
# them all in the docs
#
# https://rio.dev/docs/api/theme
theme = rio.Theme.from_colors(
    primary_color=rio.Color.from_hex("01dffdff"),
    secondary_color=rio.Color.from_hex("0083ffff"),
    mode="light",
)


# Create the Rio app
app = rio.App(
    build=HomePage,
    name=__project__,
    description=__description__,
    icon=Path(__file__).parent / "assets" / "locker.ico",
    # This function will be called once the app is ready.
    #
    # `rio run` will also call it again each time the app is reloaded.
    on_app_start=on_app_start,
    # This function will be called each time a user connects
    on_session_start=on_session_start,
    default_attachments=[],
    assets_dir=Path(__file__).parent / "assets",
    theme=theme,
)
