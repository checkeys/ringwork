# coding:utf-8

from typing import List
from typing import Literal
from typing import Optional

from rio import Button
from rio import ColorSet
from rio import Component
from rio import EventHandler
from rio import IconButton
from rio import Link
from rio import Rectangle
from rio import Row
from rio import Spacer
from rio import Tooltip
from rio import event
from rio_xpw.access import AccessControl
from rio_xpw.access import EndUser

from ringwork.components.access import Redirect


class NavbarButton(Component):

    icon: str
    content: str
    shape: Literal["pill", "rounded", "rectangle"]
    style: Literal["major", "minor", "colored-text", "plain-text"]
    color: ColorSet = "keep"
    on_press: EventHandler[[]] = None

    def build(self) -> Component:
        return Button(
            content=self.content,
            icon=self.icon,
            shape=self.shape,
            style=self.style,
            color=self.color,
            on_press=self.on_press,
        )


class NavbarIconButton(Component):

    icon: str
    content: str = ""
    style: Literal["major", "minor", "colored-text", "plain-text"] = "plain-text"  # noqa:E501
    color: ColorSet = "keep"
    on_press: EventHandler[[]] = None
    target_url: Optional[str] = None

    def __build_button(self) -> Component:
        if (target_url := self.target_url) is not None:
            selected: bool = self.session.active_page_url.raw_path == target_url  # noqa:E501
            return Link(
                content=IconButton(
                    icon=self.icon,
                    style="colored-text" if selected else "plain-text",
                ),
                target_url=target_url,
            )

        return IconButton(icon=self.icon, style=self.style, color=self.color, on_press=self.on_press)  # noqa:E501

    def build(self) -> Component:
        return Tooltip(anchor=self.__build_button(), tip=self.content) if self.content else self.__build_button()  # noqa:E501


class NavbarCommonButton(Component):

    icon: str
    content: str
    style: Literal["major", "minor", "colored-text", "plain-text"]
    color: ColorSet = "keep"
    on_press: EventHandler[[]] = None

    def build(self) -> Component:
        if self.session.window_height > 50.0:
            return NavbarButton(
                content=self.content,
                icon=self.icon,
                shape="rounded",
                style=self.style,
                color=self.color,
                on_press=self.on_press,
            )
        else:
            return Tooltip(
                anchor=NavbarIconButton(
                    icon=self.icon,
                    style="colored-text",
                    color=self.color,
                    on_press=self.on_press,
                ),
                tip=self.content,
            )


class NavbarLeftComponent(Component):

    def __post_init__(self) -> None:
        self.__children: List[Component] = []

    def add(self, child: Component) -> None:
        self.__children.append(child)

    def new_button(self, icon: str, content: str, target_url: str) -> Component:  # noqa:E501
        return NavbarIconButton(icon=icon, content=content, target_url=target_url)  # noqa:E501

    def build(self) -> Component:
        return Row(
            self.new_button(icon="material/home", content="Home", target_url="/"),  # noqa:E501
            self.new_button(icon="material/key", content="SSH Keys", target_url="/ssh"),  # noqa:E501
            self.new_button(icon="material/checklist", content="Public List", target_url="/public"),  # noqa:E501
            *self.__children,
            spacing=1.0,
            margin=0.0,
        )


class NavbarRightComponent(Component):

    def __post_init__(self) -> None:
        self.__children: List[Component] = []

    def add(self, child: Component) -> None:
        self.__children.append(child)

    async def _on_logout(self) -> None:
        access_control: AccessControl = self.session[AccessControl]
        if access_control.deactivate(user=self.session[EndUser]):
            self.session.close()

    async def _on_login(self) -> None:
        self.session.navigate_to(Redirect(self.session.active_page_url.path))

    def build(self) -> Component:
        access_control: AccessControl = self.session[AccessControl]
        if not access_control.identify(user=self.session[EndUser]):
            button = NavbarCommonButton(
                content="Login",
                icon="material/login",
                color="secondary",
                style="minor",
                on_press=self._on_login,
            )
        else:
            button = NavbarCommonButton(
                content="Logout",
                icon="material/logout",
                color="danger",
                style="minor",
                on_press=self._on_logout,
            )

        return Row(
            *self.__children,
            button,
            spacing=1.0,
            margin_y=0.5,
        )


class Navbar(Component):

    def __post_init__(self) -> None:
        self.__left_component: NavbarLeftComponent = NavbarLeftComponent()
        self.__right_component: NavbarRightComponent = NavbarRightComponent()

    @property
    def left(self) -> NavbarLeftComponent:
        return self.__left_component

    @property
    def right(self) -> NavbarRightComponent:
        return self.__right_component

    @event.on_page_change
    def on_page_change(self) -> None:
        self.force_refresh()

    def build(self) -> Component:
        return Rectangle(
            content=Row(
                self.__left_component,
                Spacer(grow_x=True),
                self.__right_component,
                grow_x=True,
                spacing=1.0,
                margin_x=1.0,
                margin_y=0.5,
            ),
            min_width=self.session.window_width - 4.0,
            grow_x=True,
            align_x=0.0,
            align_y=0.0,
            margin=2.0,
            fill=self.session.theme.neutral_color,
            corner_radius=self.session.theme.corner_radius_medium,
            shadow_radius=0.8,
            shadow_offset_y=0.2,
            shadow_color=self.session.theme.shadow_color,
        )
