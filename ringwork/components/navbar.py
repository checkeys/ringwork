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
from rio import event

from ringwork.components.access import AccessControl
from ringwork.components.access import EndUser


class NavbarButton(Component):

    icon: str
    content: str
    shape: Literal["pill", "rounded", "rectangle"]
    style: Literal["major", "minor", "colored-text", "plain-text"]
    color: ColorSet = "keep"
    on_press: EventHandler[()] = None

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
    style: Literal["major", "minor", "colored-text", "plain-text"] = "plain-text"  # noqa:E501
    color: ColorSet = "keep"
    target_url: Optional[str] = None

    def build(self) -> Component:
        if (target_url := self.target_url) is not None:
            selected: bool = self.session.active_page_url.raw_path == target_url  # noqa:E501
            return Link(
                content=IconButton(
                    icon=self.icon,
                    style="colored-text" if selected else "plain-text",
                ),
                target_url=target_url,
            )

        return IconButton(icon=self.icon, style=self.style, color=self.color)


class NavbarCommonButton(Component):

    icon: str
    content: str
    style: Literal["major", "minor", "colored-text", "plain-text"]
    color: ColorSet = "keep"
    on_press: EventHandler[()] = None

    def build(self) -> Component:
        return NavbarButton(
            content=self.content,
            icon=self.icon,
            shape="rounded",
            style=self.style,
            color=self.color,
            on_press=self.on_press,
        )


class NavbarLeftComponent(Component):

    def __post_init__(self) -> None:
        self.__children: List[Component] = []

    def add(self, child: Component) -> None:
        self.__children.append(child)

    def new_button(self, icon: str, target_url: str) -> Component:
        return NavbarIconButton(icon=icon, target_url=target_url)

    def build(self) -> Component:
        return Row(
            self.new_button(icon="material/home:fill", target_url="/"),
            self.new_button(icon="material/key:fill", target_url="/ssh"),
            self.new_button(icon="material/checklist:fill", target_url="/public"),  # noqa:E501
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
            self.session.navigate_to("/")

    async def _on_login(self) -> None:
        self.session.navigate_to("/login")

    def build(self) -> Component:
        access_control: AccessControl = self.session[AccessControl]
        if not access_control.validate(user=self.session[EndUser]):
            button = Button(
                content="Login",
                icon="material/login",
                shape="rounded",
                color="secondary",
                style="minor",
                on_press=self._on_login,
            )
        else:
            button = Button(
                content="Logout",
                icon="material/logout",
                shape="rounded",
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
