# coding:utf-8

from pathlib import Path
from typing import Optional

from rio import App
from rio import Color
from rio import Theme
from uvicorn import Config
from uvicorn import Server

from ringwork.attribute import __description__
from ringwork.attribute import __project__
from ringwork.components.access import AccessControl
from ringwork.interfaces.sshkey import PublicKeyAPI
from ringwork.pages import MainPage


def create_app(access_control: Optional[AccessControl] = None) -> App:
    if access_control is None:
        access_control = AccessControl()

    # https://rio.dev/docs/api/theme
    theme = Theme.from_colors(
        primary_color=Color.from_hex("01dffdff"),
        secondary_color=Color.from_hex("0083ffff"),
        mode="light",
    )

    # Create the Rio app
    app = App(
        build=MainPage,
        name=__project__,
        description=__description__,
        icon=Path(__file__).parent / "assets" / "favicon.ico",
        # This function will be called once the app is ready.
        #
        # `rio run` will also call it again each time the app is reloaded.
        on_app_start=access_control.on_app_start,
        # This function will be called each time a user connects
        on_session_start=access_control.on_session_start,
        default_attachments=[AccessControl.NOBODY],
        assets_dir=Path(__file__).parent / "assets",
        theme=theme,
    )

    return app


def run_as_web_server(host: str = "0.0.0.0", port: int = 8000, quiet: bool = True) -> None:  # noqa:E501
    access_control: AccessControl = AccessControl()
    public_key_api: PublicKeyAPI = PublicKeyAPI(access_control.accounts)

    fastapi_app = create_app(access_control).as_fastapi()
    fastapi_app.add_api_route(path=PublicKeyAPI.DOWNLOAD_PATH, endpoint=public_key_api.download, methods=["GET"])  # noqa:E501
    fastapi_app.add_api_route(path=PublicKeyAPI.RAW_PATH, endpoint=public_key_api.get, methods=["GET"])  # noqa:E501

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
    run_as_web_server(host="0.0.0.0", port=9000, quiet=False)
