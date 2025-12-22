# coding:utf-8

from dataclasses import dataclass
from functools import partial
from typing import Dict
from typing import Literal
from typing import get_args  # noqa:H306

from rio import Banner
from rio import Button
from rio import Card
from rio import Column
from rio import Component
from rio import CustomListItem
from rio import Dropdown
from rio import DropdownChangeEvent
from rio import EventHandler
from rio import FilePickEvent
from rio import FilePickerArea
from rio import Icon
from rio import IconButton
from rio import Link
from rio import ListView
from rio import MultiLineTextInput
from rio import MultiLineTextInputChangeEvent
from rio import NumberInput
from rio import Row
from rio import ScrollContainer
from rio import SeparatorListItem
from rio import Spacer
from rio import Text
from rio import TextInput
from rio import TextInputChangeEvent
from rio import Tooltip
from rio import event
from rio_xpw.access import AccessControl
from rio_xpw.access import EndUser
from xkeys_ssh import SSHKeyAlgo
from xkeys_ssh import SSHKeyPair
from xkeys_ssh import SSHKeyRing

from ringwork.interfaces.sshkey import PublicKeyAPI

SSHKeyTypeOptions = {key.upper(): key for key in get_args(SSHKeyAlgo)}


@dataclass
class SSHKeyItem:

    algorithm: SSHKeyAlgo
    fingerprint: str
    comment: str
    private: str
    public: str
    bits: int
    name: str
    user: str

    @classmethod
    def empty(cls) -> "SSHKeyItem":
        return cls(algorithm="rsa",
                   fingerprint="",
                   comment="",
                   private="",
                   public="",
                   bits=4096,
                   name="",
                   user="")

    @classmethod
    def create(cls, user: str, name: str, pair: SSHKeyPair) -> "SSHKeyItem":
        return cls(algorithm=pair.algo,
                   fingerprint=pair.fingerprint,
                   comment=pair.comment,
                   private=pair.private,
                   public=pair.public,
                   bits=pair.bits,
                   name=name,
                   user=user)


class KeyComponent(Component):

    item: SSHKeyItem
    on_delete: EventHandler[[]] = None

    def __post_init__(self) -> None:
        # The "public" button
        self.__public_button = Tooltip(
            anchor=Link(
                content=IconButton(
                    icon="material/info",
                    style="colored-text",
                    min_size=3.0,
                ),
                target_url=PublicKeyAPI.get_raw_url(uid=self.item.user, kid=self.item.name),  # noqa:E501
                open_in_new_tab=True,
            ),
            tip="Display public key",
        )

        # The "delete" button
        self.__delete_button = Tooltip(
            anchor=IconButton(
                icon="material/delete",
                on_press=self.on_delete,
                style="colored-text",
                color="danger",
                min_size=3.0,
            ),
            tip="Delete",
        )

    def _build_view(self) -> Component:
        return ListView(
            CustomListItem(
                content=Row(
                    Column(
                        Text(
                            "Private key",
                            selectable=False,
                            style="heading3",
                            justify="left",
                        ),
                        ScrollContainer(
                            content=Text(
                                self.item.private,
                                overflow="ellipsize",
                                selectable=False,
                                justify="left",
                                style="dim",
                            ),
                            min_height=10.0,
                            scroll_x="never",
                            scroll_y="auto",
                        ),
                        spacing=0.5,
                        grow_x=True,
                        align_y=0.5,  # In case too much space is allocated
                    ),
                    Tooltip(
                        anchor=IconButton(
                            icon="material/download",
                            on_press=lambda: self.session.save_file(
                                file_contents=self.item.private,
                                file_name=f"{self.item.name}",
                                media_type="application/octet-stream",
                            ),
                            style="plain-text",
                            min_size=3.0,
                        ),
                        tip="Download private key file",
                    ),
                    Tooltip(
                        anchor=IconButton(
                            icon="material/content_copy",
                            on_press=lambda: self.session.set_clipboard(
                                self.item.private
                            ),
                            style="plain-text",
                            min_size=3.0,
                        ),
                        tip="Copy private key to clipboard",
                    ),
                    grow_x=True,
                ),
                key="private",
            ),
            SeparatorListItem(),
            CustomListItem(
                content=Row(
                    Column(
                        Text(
                            "Public key",
                            selectable=False,
                            style="heading3",
                            justify="left",
                        ),
                        Text(
                            self.item.public,
                            overflow="ellipsize",
                            selectable=False,
                            justify="left",
                            style="dim",
                        ),
                        spacing=0.5,
                        grow_x=True,
                        align_y=0.5,  # In case too much space is allocated
                    ),
                    Tooltip(
                        anchor=Link(
                            content=IconButton(
                                icon="material/download",
                                style="plain-text",
                                min_size=3.0,
                            ),
                            target_url=PublicKeyAPI.get_download_url(uid=self.item.user, kid=self.item.name),  # noqa:E501
                            open_in_new_tab=True,
                        ),
                        tip="Download public key file",
                    ),
                    Tooltip(
                        anchor=IconButton(
                            icon="material/content_copy",
                            on_press=lambda: self.session.set_clipboard(
                                self.item.public
                            ),
                            style="plain-text",
                            min_size=3.0,
                        ),
                        tip="Copy public key to clipboard",
                    ),
                    grow_x=True,
                ),
                key="public",
            ),
            SeparatorListItem(),
            align_y=0,
        )

    async def _on_click(self) -> None:
        """Creates a dialog to display a menu item."""

        def build_dialog_content() -> Component:
            if (window_width := self.session.window_width) < 60.0:
                min_width = window_width - 10.0
            else:
                min_width = 50.0

            return Column(
                Text(self.item.name, style="heading2"),
                self._build_view(),
                Tooltip(
                    anchor=IconButton(
                        icon="material/close",
                        on_press=lambda: dialog.close(None),
                        color="danger",
                        style="minor",
                        min_size=3.0,
                        # align_y=1.0,
                    ),
                    tip="Close",
                ),
                min_width=min_width,
                spacing=1.0,
            )

        # Show the dialog
        dialog = await self.session.show_custom_dialog(
            build=build_dialog_content,
            # Prevent the user from interacting with the rest of the app
            # while the dialog is open
            modal=True,
            # Close the dialog if the user clicks outside of it
            user_closable=True,
        )

        # Wait for the user to select an option
        await dialog.wait_for_close()

    def build(self) -> Component:
        status_icon = Icon(
            "material/key",
            fill="success",
            min_height=2.5,
            min_width=2.5,
        )

        identifier = Column(Text(self.item.name, style="heading3"))
        if self.session.window_width > 50.0:
            identifier.add(Text(self.item.fingerprint, style="dim"))

        return Card(
            Row(
                status_icon,
                Spacer(min_width=0.5, grow_x=False),
                identifier,  # The name and fingerprint
                Spacer(grow_x=True),
                self.__public_button,
                self.__delete_button,
                spacing=0.5,
                margin=0.5,
            ),
            on_press=self._on_click,
            color="background",
            elevate_on_hover=True,
            corner_radius=9999,
        )


class CreateComponent(Component):

    item: SSHKeyItem
    on_finish: EventHandler[[]]

    def __post_init__(self) -> None:
        self.__banner_text: str = ""
        self.__sync_name: bool = True
        self.__sync_comment: bool = True

    def _on_change_name(self, ev: TextInputChangeEvent) -> None:
        self.__sync_name = not ev.text
        self.item.name = ev.text

        if self.__sync_comment and ev.text:
            self.item.comment = ev.text
            self.force_refresh()

    def _on_change_comment(self, ev: TextInputChangeEvent) -> None:
        self.__sync_comment = not ev.text
        self.item.comment = ev.text

        if self.__sync_name and ev.text:
            self.item.name = ev.text
            self.force_refresh()

    def _on_change_algorithm(self, ev: DropdownChangeEvent) -> None:
        self.item.algorithm = ev.value
        if ev.value == "rsa":
            self.item.bits = 4096
        self.force_refresh()

    async def _on_press_cancel(self) -> None:
        self.item.name = ""

        await self.call_event_handler(self.on_finish)

    async def _on_press_create(self) -> None:
        if not self.item.name:
            self.__banner_text = "Please enter a name"
            return self.force_refresh()

        if not self.item.comment:
            self.__banner_text = "Please enter a comment"
            return self.force_refresh()

        access_control: AccessControl = self.session[AccessControl]
        if not (profile := access_control.identify(user=self.session[EndUser])):  # noqa:E501
            self.__banner_text = "Login required"
            return self.force_refresh()

        if self.item.name in (ring := SSHKeyRing(base=profile.workspace)):
            self.__banner_text = "SSH key already exists"
            return self.force_refresh()

        try:
            if not ring.generate(algo=self.item.algorithm, bits=self.item.bits,
                                 name=self.item.name, comment=self.item.comment):  # noqa:E501
                self.__banner_text = "Failed to generate SSH key"
                return self.force_refresh()
        except Exception as error:
            self.__banner_text = str(error)
            return self.force_refresh()

        await self.call_event_handler(self.on_finish)

    def build(self) -> Component:
        if (window_width := self.session.window_width) < 50.0:
            min_width = window_width - 10.0
        else:
            min_width = 30.0

        content = Column(
            Text(
                text="Generate new SSH key",
                style="heading2",
            ),
            Banner(text=self.__banner_text, style="danger"),
            TextInput(
                on_change=self._on_change_name,
                text=self.item.name,
                label="Name",
            ),
            TextInput(
                on_change=self._on_change_comment,
                text=self.item.comment,
                label="Comment",
            ),
            Dropdown(
                on_change=self._on_change_algorithm,
                selected_value=self.item.algorithm,
                options=SSHKeyTypeOptions,
                label="Algorithm",
            ),
            min_width=min_width,
            spacing=1.0,
        )

        if self.item.algorithm == "rsa":
            self.item.bits = max(1024, self.item.bits)
            content.add(
                NumberInput(
                    on_change=lambda e: setattr(self.item, "bits", int(e.value)),  # noqa:E501
                    value=self.item.bits,
                    label="Bits",
                    minimum=1024,
                    decimals=0,
                )
            )
        elif self.item.algorithm == "dsa":
            self.item.bits = 1024
            content.add(
                NumberInput(
                    value=self.item.bits,
                    is_sensitive=False,
                    label="Bits",
                    decimals=0,
                )
            )
        elif self.item.algorithm == "ecdsa":
            self.item.bits = 521
            content.add(
                Dropdown(
                    on_change=lambda e: setattr(self.item, "bits", e.value),
                    selected_value=self.item.bits,
                    options=[256, 384, 521],
                    label="Bits",
                )
            )

        content.add(
            Row(
                Button(
                    "Cancel",
                    color="danger",
                    style="minor",
                    on_press=self._on_press_cancel,
                ),
                Button(
                    "Generate",
                    color="keep",
                    style="major",
                    on_press=self._on_press_create,
                ),
                spacing=1.0,
            )
        )

        return content


class UploadComponent(Component):

    item: SSHKeyItem
    on_finish: EventHandler[[]]

    def __post_init__(self) -> None:
        self.__banner_text: str = ""

    def _on_change_name(self, ev: TextInputChangeEvent) -> None:
        self.item.name = ev.text

    def _on_change_private(self, ev: MultiLineTextInputChangeEvent) -> None:
        self.item.private = ev.text

        if not self.item.name:
            try:
                self.item.name = SSHKeyPair(private=ev.text).comment or self.item.name  # noqa:E501
                self.force_refresh()
            except Exception:
                pass

    async def _on_pick_file(self, ev: FilePickEvent) -> None:
        try:
            text = await ev.file.read_text(encoding="utf-8")
            pair = SSHKeyPair(private=text)
            self.item.name = pair.comment
            self.item.private = pair.private
            self.__banner_text = ""
        except Exception:
            self.__banner_text = "Invalid private key file"

        self.force_refresh()

    async def _on_press_cancel(self) -> None:
        self.item.name = ""

        await self.call_event_handler(self.on_finish)

    async def _on_press_save(self) -> None:
        if not self.item.name:
            self.__banner_text = "Please enter a name"
            return self.force_refresh()

        if not self.item.private:
            self.__banner_text = "Please enter a private key"
            return self.force_refresh()

        access_control: AccessControl = self.session[AccessControl]
        if not (profile := access_control.identify(user=self.session[EndUser])):  # noqa:E501
            self.__banner_text = "Login required"
            return self.force_refresh()

        if self.item.name in (ring := SSHKeyRing(base=profile.workspace)):
            self.__banner_text = "SSH key already exists"
            return self.force_refresh()

        try:
            self.item.name = ring.create(private=self.item.private, name=self.item.name)  # noqa:E501
        except Exception as error:
            self.__banner_text = str(error)
            return self.force_refresh()

        await self.call_event_handler(self.on_finish)

    def build(self) -> Component:
        if (window_width := self.session.window_width) < 50.0:
            min_width = window_width - 10.0
        else:
            min_width = 30.0

        content = Column(
            Text(text="Upload SSH key", style="heading2", grow_x=True),
            Banner(text=self.__banner_text, style="danger"),
            TextInput(
                on_change=self._on_change_name,
                text=self.item.name,
                label="Name",
            ),
            MultiLineTextInput(
                on_change=self._on_change_private,
                auto_adjust_height=False,
                text=self.item.private,
                label="Private key",
                # min_height=15.0,
            ),
            FilePickerArea(
                content="Upload file" if min_width < 30.0 else "Drag & Drop private key file here",  # noqa:E501
                file_types=None,
                multiple=False,
                on_pick_file=self._on_pick_file,
            ),
            min_width=min_width,
            spacing=1.0,
        )

        content.add(
            Row(
                Button(
                    "Cancel",
                    color="danger",
                    style="minor",
                    on_press=self._on_press_cancel,
                ),
                Button(
                    "Save",
                    color="keep",
                    style="major",
                    on_press=self._on_press_save,
                ),
                spacing=1.0,
            )
        )

        return content


class ListComponent(Component):

    def __post_init__(self) -> None:
        self.__banner_style: Literal["success", "danger", "info"] = "success"
        self.__banner_text: str = ""

        self.__ssh_keys: Dict[str, SSHKeyItem] = {}

    def _cleanup_prompt(self) -> None:
        self.__banner_style = "success"
        self.__banner_text = ""

    def _success_prompt(self, text: str) -> None:
        self.__banner_style = "success"
        self.__banner_text = text

    def _danger_prompt(self, text: str) -> None:
        self.__banner_style = "danger"
        self.__banner_text = text

    def _prompt(self, text: str) -> None:
        self.__banner_style = "info"
        self.__banner_text = text

    @event.on_populate
    def on_populate(self) -> None:
        """Event handler that is called when the component is populated.

        Fetches data from a predefined data model and assigns it to the
        ssh_keys attribute of the current instance.
        """
        access_control: AccessControl = self.session[AccessControl]
        if profile := access_control.identify(user=self.session[EndUser]):
            for name in (ring := SSHKeyRing(base=profile.workspace)):
                self.__add_item(SSHKeyItem.create(profile.username, name, ring[name]))  # noqa:E501

    def __add_item(self, item: SSHKeyItem) -> None:
        if (name := item.name) not in self.__ssh_keys:
            self.__ssh_keys[name] = item

    def __del_item(self, name: str) -> None:
        if name in self.__ssh_keys:
            del self.__ssh_keys[name]

    async def create_item(self) -> None:
        new_item: SSHKeyItem = SSHKeyItem.empty()

        async def refresh() -> None:
            if name := new_item.name:
                access_control: AccessControl = self.session[AccessControl]
                if profile := access_control.identify(user=self.session[EndUser]):  # noqa:E501
                    pair: SSHKeyPair = SSHKeyRing(base=profile.workspace)[name]
                    self.__add_item(SSHKeyItem.create(profile.username, name, pair))  # noqa:E501
                    self._success_prompt(f"SSH key '{name}' generated")
            await dialog.close(None)
            self.force_refresh()

        def build_dialog_content() -> Component:
            return CreateComponent(item=new_item, on_finish=refresh)

        # Show the dialog
        dialog = await self.session.show_custom_dialog(
            build=build_dialog_content,
            # Prevent the user from interacting with the rest of the app
            # while the dialog is open
            modal=True,
            # Don't close the dialog if the user clicks outside of it
            user_closable=False,
        )

        # Wait for the user to select an option
        await dialog.wait_for_close()

    async def upload_item(self) -> None:
        new_item: SSHKeyItem = SSHKeyItem.empty()

        async def refresh() -> None:
            if name := new_item.name:
                access_control: AccessControl = self.session[AccessControl]
                if profile := access_control.identify(user=self.session[EndUser]):  # noqa:E501
                    pair: SSHKeyPair = SSHKeyRing(base=profile.workspace)[name]
                    self.__add_item(SSHKeyItem.create(profile.username, name, pair))  # noqa:E501
                    self._success_prompt(f"SSH key '{name}' saved")
            await dialog.close(None)
            self.force_refresh()

        def build_dialog_content() -> Component:
            return UploadComponent(item=new_item, on_finish=refresh)

        # Show the dialog
        dialog = await self.session.show_custom_dialog(
            build=build_dialog_content,
            # Prevent the user from interacting with the rest of the app
            # while the dialog is open
            modal=True,
            # Don't close the dialog if the user clicks outside of it
            user_closable=False,
        )

        # Wait for the user to select an option
        await dialog.wait_for_close()

    async def _delete_item(self, name: str) -> None:
        """Perform actions when the "Delete" button is pressed."""

        async def confirm_delete() -> None:
            access_control: AccessControl = self.session[AccessControl]
            if profile := access_control.identify(user=self.session[EndUser]):
                if SSHKeyRing(base=profile.workspace).remove(name):
                    self._success_prompt(f"Successfully deleted {name}")
                    self.__del_item(name)
                else:
                    self._danger_prompt(f"Failed to delete {name}")
            else:
                self._danger_prompt("Login required")
            self.force_refresh()

            await dialog.close(None)

        async def cancel_delete() -> None:
            await dialog.close(None)

        def build_confirmation_dialog() -> Component:
            return Column(
                Row(
                    Text(text=f"Delete {name}", style="heading2"),
                    Spacer(grow_x=True),
                    Tooltip(
                        anchor=IconButton(
                            icon="material/close",
                            on_press=cancel_delete,
                            style="colored-text",
                            color="keep",
                            min_size=3.0,
                        ),
                        tip="Cancel and close dialog",
                    ),
                ),
                Banner(text="Unexpected bad things will happen if you don’t read this!", style="danger"),  # noqa:E501
                Column(
                    Text(text=f"This will permanently delete the \"{name}\" SSH private key.", style="text"),  # noqa:E501
                    Text(text="You can still use this SSH key if it has already been stored.", style="text"),  # noqa:E501
                    Text(text="But if you want to create it again, you must have the private key.", style="text"),  # noqa:E501
                    spacing=0.5,
                ),
                Button(
                    "I have read and understand these effects",
                    style="minor",
                    color="danger",
                    on_press=confirm_delete,
                ),
                spacing=1.0,
            )

        # Show confirmation dialog
        dialog = await self.session.show_custom_dialog(
            build=build_confirmation_dialog,
            # Prevent the user from interacting with the rest of the app
            # while the dialog is open
            modal=True,
            # Close the dialog if the user clicks outside of it
            user_closable=True,
        )

        await dialog.wait_for_close()

    def build(self) -> Component:
        return Column(
            Text(text="SSH Keys", style="heading2"),
            Banner(self.__banner_text, style=self.__banner_style),
            *[
                KeyComponent(
                    item=item,
                    on_delete=partial(self._delete_item, name),
                )
                for name, item in self.__ssh_keys.items()
            ],
            spacing=1.0,
        )
