from pathlib import Path

import rio
from xpw import Account
from xpw import SessionID

from ringwork.attribute import __description__
from ringwork.attribute import __project__
from ringwork.components.user import UserSettings
from ringwork.pages import MainPage


async def on_app_start(app: rio.App) -> None:
    account: Account = Account.from_file()
    app.default_attachments.append(account)


async def on_session_start(rio_session: rio.Session) -> None:
    setting: UserSettings = rio_session[UserSettings]
    if not setting.session_id:
        setting.session_id = SessionID.generate()
        rio_session.attach(setting)


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
    build=MainPage,
    name=__project__,
    description=__description__,
    icon=Path(__file__).parent / "assets" / "favicon.ico",
    # This function will be called once the app is ready.
    #
    # `rio run` will also call it again each time the app is reloaded.
    on_app_start=on_app_start,
    # This function will be called each time a user connects
    on_session_start=on_session_start,
    default_attachments=[UserSettings(session_id="", secret_key="")],
    assets_dir=Path(__file__).parent / "assets",
    theme=theme,
)
