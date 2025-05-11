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
from rio import HeadingListItem
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
from rio import Text
from rio import TextInput
from rio import TextInputChangeEvent
from rio import Tooltip
from rio import event
from xkeys_ssh import SSHKeyAlgo
from xkeys_ssh import SSHKeyPair
from xkeys_ssh import SSHKeyRing
from xpw import Account

from ringwork.components.access import EndUser
from ringwork.components.navbar import Navbar

SSHKeyTypeOptions = {key.upper(): key for key in get_args(SSHKeyAlgo)}


@dataclass
class SSHKeyItem:
    """SSHKeyItem data model."""

    algorithm: SSHKeyAlgo
    fingerprint: str
    comment: str
    private: str
    public: str
    bits: int
    name: str

    @classmethod
    def empty(cls) -> "SSHKeyItem":
        """Creates a new empty SSHKeyItem object."""
        return cls(algorithm="rsa",
                   fingerprint="",
                   comment="",
                   private="",
                   public="",
                   bits=4096,
                   name="")

    @classmethod
    def create(cls, name: str, pair: SSHKeyPair) -> "SSHKeyItem":
        return cls(algorithm=pair.algo,
                   fingerprint=pair.fingerprint,
                   comment=pair.comment,
                   private=pair.private,
                   public=pair.public,
                   bits=pair.bits,
                   name=name)


class KeyItemComponent(Component):
    """Displays a single `SSHKeyItem`."""

    item: SSHKeyItem
    on_delete: EventHandler[[]] = None

    def build_list_view(self) -> Component:
        return ListView(
            HeadingListItem(text=self.item.name, key="heading"),
            SeparatorListItem(),
            CustomListItem(
                content=Row(
                    Column(
                        Text(
                            "Private key",
                            justify="left",
                            selectable=False,
                        ),
                        ScrollContainer(
                            content=Text(
                                self.item.private,
                                style="dim",
                                justify="left",
                                selectable=False,
                            ),
                            scroll_x="never",
                            scroll_y="auto",
                        ),
                        spacing=0.5,
                        grow_x=True,
                        align_y=0.5,  # In case too much space is allocated
                    ),
                    IconButton(
                        icon="material/download",
                        on_press=lambda: self.session.save_file(
                            file_contents=self.item.private,
                            file_name=f"{self.item.name}",
                            media_type="application/octet-stream",
                        ),
                        style="plain-text",
                        min_size=3.0,
                    ),
                    IconButton(
                        icon="material/content_copy",
                        on_press=lambda: self.session.set_clipboard(
                            self.item.private
                        ),
                        style="plain-text",
                        min_size=3.0,
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
                            justify="left",
                            selectable=False,
                        ),
                        Text(
                            self.item.public,
                            overflow="ellipsize",
                            style="dim",
                            justify="left",
                            selectable=False,
                        ),
                        spacing=0.5,
                        grow_x=True,
                        align_y=0.5,  # In case too much space is allocated
                    ),
                    IconButton(
                        icon="material/download",
                        on_press=lambda: self.session.save_file(
                            file_contents=self.item.public,
                            file_name=f"{self.item.name}.pub",
                            media_type="application/octet-stream",
                        ),
                        style="plain-text",
                        min_size=3.0,
                    ),
                    IconButton(
                        icon="material/content_copy",
                        on_press=lambda: self.session.set_clipboard(
                            self.item.public
                        ),
                        style="plain-text",
                        min_size=3.0,
                    ),
                    grow_x=True,
                ),
                key="public",
            ),
            SeparatorListItem(),
            align_y=0,
        )

    async def on_click(self) -> None:
        """Creates a dialog to display a menu item."""

        def build_dialog_content() -> Component:
            return Column(
                self.build_list_view(),
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
        return Card(
            Row(
                Icon(
                    "material/key",
                    fill="success",
                    min_height=2.5,
                    min_width=2.5,
                ),
                # The name and fingerprint
                Column(
                    Text(self.item.name),
                    Text(self.item.fingerprint),
                    # Let the title grow to fill the available space
                    grow_x=True,
                ),
                # The "copy" button
                Tooltip(
                    anchor=IconButton(
                        icon="material/content_copy",
                        on_press=lambda: self.session.set_clipboard(
                            self.item.public
                        ),
                        color="keep",
                        style="colored-text",
                        min_size=3.0,
                    ),
                    tip="Copy public key",
                ),
                # The "delete" button
                Tooltip(
                    anchor=IconButton(
                        icon="material/delete",
                        on_press=self.on_delete,
                        color="danger",
                        style="colored-text",
                        min_size=3.0,
                    ),
                    tip="Delete",
                ),
                spacing=0.5,
                margin=0.5,
            ),
            on_press=self.on_click,
            color="background",
            elevate_on_hover=True,
            corner_radius=9999,
        )


class CreateComponent(Component):

    item: SSHKeyItem
    on_finish: EventHandler[[]] = None

    sync_name: bool = True
    sync_comment: bool = True

    banner_text: str = ""

    def _on_change_name(self, ev: TextInputChangeEvent) -> None:
        self.sync_name = not ev.text
        self.item.name = ev.text

        if self.sync_comment and ev.text:
            self.item.comment = ev.text
            self.force_refresh()

    def _on_change_comment(self, ev: TextInputChangeEvent) -> None:
        self.sync_comment = not ev.text
        self.item.comment = ev.text

        if self.sync_name and ev.text:
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
            self.banner_text = "Please enter a name"
            return self.force_refresh()

        if not self.item.comment:
            self.banner_text = "Please enter a comment"
            return self.force_refresh()

        account: Account = self.session[Account]
        enduser: EndUser = self.session[EndUser]
        if not (profile := account.fetch(enduser.session_id, enduser.secret_key)):  # noqa:E501
            self.banner_text = "Login required"
            return self.force_refresh()

        if self.item.name in (ring := SSHKeyRing(base=profile.workspace)):
            self.banner_text = "SSH key already exists"
            return self.force_refresh()

        try:
            if not ring.generate(algo=self.item.algorithm, bits=self.item.bits,
                                 name=self.item.name, comment=self.item.comment):  # noqa:E501
                self.banner_text = "Failed to generate SSH key"
                return self.force_refresh()
        except Exception as error:
            self.banner_text = str(error)
            return self.force_refresh()

        await self.call_event_handler(self.on_finish)

    def build(self) -> Component:
        content = Column(
            Text(
                text="Generate new SSH key",
                style="heading2",
            ),
            Banner(text=self.banner_text, style="danger"),
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
            min_width=30.0,
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
    on_finish: EventHandler[[]] = None

    banner_text: str = ""

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
            self.banner_text = ""
        except Exception:
            self.banner_text = "Invalid private key file"

        self.force_refresh()

    async def _on_press_save(self) -> None:
        if not self.item.name:
            self.banner_text = "Please enter a name"
            return self.force_refresh()

        if not self.item.private:
            self.banner_text = "Please enter a private key"
            return self.force_refresh()

        account: Account = self.session[Account]
        enduser: EndUser = self.session[EndUser]
        if not (profile := account.fetch(enduser.session_id, enduser.secret_key)):  # noqa:E501
            self.banner_text = "Login required"
            return self.force_refresh()

        if self.item.name in (ring := SSHKeyRing(base=profile.workspace)):
            self.banner_text = "SSH key already exists"
            return self.force_refresh()

        try:
            self.item.name = ring.create(private=self.item.private, name=self.item.name)  # noqa:E501
        except Exception:
            self.banner_text = "Failed to save SSH key"
            return self.force_refresh()

        await self.call_event_handler(self.on_finish)

    def build(self) -> Component:
        content = Column(
            Text(text="Upload SSH key", style="heading2", grow_x=True),
            Banner(text=self.banner_text, style="danger"),
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
                content="Drag & Drop private key file here",
                file_types=None,
                multiple=False,
                on_pick_file=self._on_pick_file,
            ),
            min_width=30.0,
            spacing=1.0,
        )

        content.add(
            Row(
                Button(
                    "Cancel",
                    color="danger",
                    style="minor",
                    on_press=self.on_finish,
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


class SSHKeyComponent(Component):
    """A CRUD page that allows users to create, read, update, and delete menu
    items.
    """

    banner_text: str = ""
    banner_style: Literal["success", "danger", "info"] = "success"

    ssh_keys: Dict[str, SSHKeyItem] = {}

    @event.on_populate
    def on_populate(self) -> None:
        """Event handler that is called when the component is populated.

        Fetches data from a predefined data model and assigns it to the
        ssh_keys attribute of the current instance.
        """
        account: Account = self.session[Account]
        enduser: EndUser = self.session[EndUser]
        if profile := account.fetch(enduser.session_id, enduser.secret_key):
            for name in (ring := SSHKeyRing(base=profile.workspace)):
                self.ssh_keys[name] = SSHKeyItem.create(name, ring[name])

    async def on_press_create_item(self) -> None:
        new_item: SSHKeyItem = SSHKeyItem.empty()

        async def refresh_page() -> None:
            if name := new_item.name:
                account: Account = self.session[Account]
                enduser: EndUser = self.session[EndUser]
                if profile := account.fetch(enduser.session_id, enduser.secret_key):  # noqa:E501
                    ring = SSHKeyRing(base=profile.workspace)
                    self.ssh_keys[name] = SSHKeyItem.create(name, ring[name])
            await dialog.close(None)
            self.force_refresh()

        def build_dialog_content() -> Component:
            return CreateComponent(item=new_item, on_finish=refresh_page)

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

    async def on_press_upload_item(self) -> None:
        new_item: SSHKeyItem = SSHKeyItem.empty()

        async def refresh_page() -> None:
            if name := new_item.name:
                account: Account = self.session[Account]
                enduser: EndUser = self.session[EndUser]
                if profile := account.fetch(enduser.session_id, enduser.secret_key):  # noqa:E501
                    ring = SSHKeyRing(base=profile.workspace)
                    self.ssh_keys[name] = SSHKeyItem.create(name, ring[name])
            await dialog.close(None)
            self.force_refresh()

        def build_dialog_content() -> Component:
            return UploadComponent(item=new_item, on_finish=refresh_page)

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

    async def on_press_delete_item(self, name: str) -> None:
        """Perform actions when the "Delete" button is pressed."""
        account: Account = self.session[Account]
        enduser: EndUser = self.session[EndUser]
        if profile := account.fetch(enduser.session_id, enduser.secret_key):
            ring: SSHKeyRing = SSHKeyRing(base=profile.workspace)
            if ring.remove(name):
                del self.ssh_keys[name]
                self.banner_text = f"Successfully deleted {name}"
                self.banner_style = "success"
            else:
                self.banner_text = f"Failed to delete {name}"
                self.banner_style = "danger"
        else:
            self.banner_text = "Login required"
            self.banner_style = "danger"
        self.force_refresh()

    def build(self) -> Component:
        """Builds the component to be rendered."""

        # Then unpack the list to pass the children to the ListView
        return Column(
            Navbar(
                left_children=[
                    Link(
                        content=IconButton(
                            icon="material/lists:fill",
                            style="plain-text",
                            min_size=2.5,
                        ),
                        target_url="/public",
                    ),
                ],
                right_children=[
                    Button(
                        content="Create",
                        icon="material/add",
                        color="success",
                        shape="rounded",
                        style="minor",
                        on_press=self.on_press_create_item,
                    ),
                    Button(
                        content="Upload",
                        icon="material/upload",
                        color="secondary",
                        shape="rounded",
                        style="minor",
                        on_press=self.on_press_upload_item,
                    ),
                ]
            ),
            Column(
                Text(text="SSH keys", style="heading2"),
                Banner(self.banner_text, style=self.banner_style),
                *[
                    KeyItemComponent(
                        item=item,
                        on_delete=partial(self.on_press_delete_item, name),
                    )
                    for name, item in self.ssh_keys.items()
                ],
                # align at the top
                align_y=0.0,
                grow_y=True,
                spacing=1.0,
                margin_x=3.0,
            ),
        )
