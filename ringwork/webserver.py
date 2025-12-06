# coding:utf-8

from pathlib import Path

from rio import App
from rio import Color
from rio import Session
from rio import Theme
from uvicorn import Config
from uvicorn import Server
from xpw import Account
from xpw import SessionID

from ringwork.attribute import __description__
from ringwork.attribute import __project__
from ringwork.components.access import EndUser
from ringwork.interfaces import download_public_key
from ringwork.interfaces import get_public_key
from ringwork.interfaces import get_public_list
from ringwork.pages import MainPage


async def on_app_start(app: App) -> None:
    account: Account = Account.from_file()
    app.default_attachments.append(account)


async def on_session_start(rio_session: Session) -> None:
    enduser: EndUser = rio_session[EndUser]
    if not enduser.session_id:
        enduser.session_id = SessionID.generate()
        rio_session.attach(enduser)


def run_as_web_server(host: str = "0.0.0.0", port: int = 8000, quiet: bool = True) -> None:  # noqa:E501
    # https://rio.dev/docs/api/theme
    theme = Theme.from_colors(
        primary_color=Color.from_hex("01dffdff"),
        secondary_color=Color.from_hex("0083ffff"),
        mode="light",
    )

    # Create the Rio app
    rio_app = App(
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
        default_attachments=[EndUser(session_id="", secret_key="")],
        assets_dir=Path(__file__).parent / "assets",
        theme=theme,
    )

    fastapi_app = rio_app.as_fastapi()
    fastapi_app.add_api_route(path="/api/pub/{uid}/{kid}", endpoint=get_public_key, methods=["GET"])  # noqa:E501
    fastapi_app.add_api_route(path="/api/list/{pid}", endpoint=get_public_list, methods=["GET"])  # noqa:E501
    fastapi_app.add_api_route(path="/api/download/pub/{uid}/{kid}", endpoint=download_public_key, methods=["GET"])  # noqa:E501

    config = Config(
        fastapi_app,
        host=host,
        port=port,
        # Suppress stdout messages if requested
        log_level="error" if quiet else "info",
        # Without a timeout, sometimes the server just deadlocks
        timeout_graceful_shutdown=1,
    )

    server = Server(config)
    return server.run()


if __name__ == "__main__":
    run_as_web_server(host="0.0.0.0", port=8000, quiet=False)
