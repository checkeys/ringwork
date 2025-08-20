import copy
import dataclasses
import functools
from typing import List
from typing import Literal
from typing import Optional
from typing import get_args  # noqa:H306

import rio
from xpw import Account
from xpw_keys import SSHKeyPair
from xpw_keys import SSHKeyRing
from xpw_keys import SSHKeyType

from ringwork.components.navbar import Navbar
from ringwork.components.user import UserSettings

SSHKeyTypeOptions = {key.upper(): key for key in get_args(SSHKeyType)}


@dataclasses.dataclass
class KeyItem:
    """KeyItem data model."""

    fingerprint: str
    comment: str
    private: str
    public: str
    type: SSHKeyType
    bits: int
    name: str

    def copy(self) -> "KeyItem":
        """Creates a copy of the KeyItem object."""
        return copy.copy(self)

    @classmethod
    def empty(cls) -> "KeyItem":
        """Creates a new empty KeyItem object."""
        return cls(fingerprint="",
                   comment="",
                   private="",
                   public="",
                   type="rsa",
                   bits=4096,
                   name="")

    @classmethod
    def create(cls, name: str, pair: SSHKeyPair) -> "KeyItem":
        return cls(fingerprint=pair.fingerprint,
                   comment=pair.comment,
                   private=pair.private,
                   public=pair.public,
                   type=pair.type,
                   bits=pair.bits,
                   name=name)


class KeyItemComponent(rio.Component):
    """Displays a single `KeyItem`."""

    item: KeyItem
    # on_completed: rio.EventHandler[[]] = None
    on_delete: rio.EventHandler[[]] = None

    # async def _mark_as_completed(self) -> None:
    #     # If it's already completed, there's nothing to do
    #     if self.todo_item.completed:
    #         return

    #     self.todo_item.completed = True
    #     await self.call_event_handler(self.on_completed)

    #     # Rio doesn't know that we modified the TodoItem, so it won't
    #     # automatically rebuild this component. We have to manually trigger a
    #     # rebuild.
    #     self.force_refresh()

    def build_list_view(self) -> rio.Component:
        return rio.ListView(
            rio.HeadingListItem(text=self.item.name, key="heading"),
            rio.SeparatorListItem(),
            rio.CustomListItem(
                content=rio.Row(
                    rio.Column(
                        rio.Text(
                            "Private key",
                            justify="left",
                            selectable=False,
                        ),
                        rio.ScrollContainer(
                            content=rio.Text(
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
                    rio.IconButton(
                        icon="material/download",
                        on_press=lambda: self.session.save_file(
                            file_contents=self.item.private,
                            file_name=f"{self.item.name}.key",
                        ),
                        style="plain-text",
                        min_size=3.0,
                    ),
                    rio.IconButton(
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
            rio.SeparatorListItem(),
            rio.CustomListItem(
                content=rio.Row(
                    rio.Column(
                        rio.Text(
                            "Public key",
                            justify="left",
                            selectable=False,
                        ),
                        rio.Text(
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
                    rio.IconButton(
                        icon="material/download",
                        on_press=lambda: self.session.save_file(
                            file_contents=self.item.public,
                            file_name=f"{self.item.name}.pub",
                        ),
                        style="plain-text",
                        min_size=3.0,
                    ),
                    rio.IconButton(
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
            rio.SeparatorListItem(),
            # rio.SimpleListItem(
            #     text="Fingerprint",
            #     secondary_text=self.item.fingerprint,
            #     key="fingerprint",
            # ),
            # rio.SeparatorListItem(),
            # rio.SimpleListItem(
            #     text="Comment",
            #     secondary_text=self.item.comment,
            #     key="comment",
            # ),
            # rio.SeparatorListItem(),
            # rio.SimpleListItem(
            #     text="Type",
            #     secondary_text=self.item.type,
            #     key="type",
            # ),
            # rio.SeparatorListItem(),
            # rio.SimpleListItem(
            #     text="Bits",
            #     secondary_text=str(self.item.bits),
            #     key="bits",
            # ),
            # rio.SeparatorListItem(),
            align_y=0,
        )

    async def on_click(self) -> None:
        """Creates a dialog to display a menu item."""

        def build_dialog_content() -> rio.Component:
            return rio.Column(
                self.build_list_view(),
                rio.Tooltip(
                    anchor=rio.IconButton(
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

    def build(self) -> rio.Component:
        return rio.Card(
            rio.Row(
                rio.Icon(
                    "material/key",
                    fill="success",
                    min_height=2.5,
                    min_width=2.5,
                ),
                # The name and fingerprint
                rio.Column(
                    rio.Text(self.item.name),
                    rio.Text(self.item.fingerprint),
                    # Let the title grow to fill the available space
                    grow_x=True,
                ),
                # The "delete" button
                rio.Tooltip(
                    anchor=rio.IconButton(
                        icon="material/delete",
                        on_press=self.on_delete,
                        color="danger",
                        style="minor",
                        min_size=2.5,
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


class AddKeyItemComponent(rio.Component):
    """Displays a single `KeyItem`."""

    item: KeyItem
    on_save: rio.EventHandler[[]] = None

    sync_name: bool = True
    sync_comment: bool = True

    def on_change_name(self, ev: rio.TextInputChangeEvent) -> None:
        self.sync_name = not ev.text
        self.item.name = ev.text

        if self.sync_comment and ev.text:
            self.item.comment = ev.text
            self.force_refresh()

    def on_change_comment(self, ev: rio.TextInputChangeEvent) -> None:
        self.sync_comment = not ev.text
        self.item.comment = ev.text

        if self.sync_name and ev.text:
            self.item.name = ev.text
            self.force_refresh()

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text(
                text="Add SSH key",
                style="heading2",
            ),
            rio.TextInput(
                on_change=self.on_change_name,
                text=self.item.name,
                label="Name",
            ),
            rio.TextInput(
                on_change=self.on_change_comment,
                text=self.item.comment,
                label="Comment",
            ),
            rio.Dropdown(
                on_change=lambda e: setattr(self.item, "type", e.value),
                selected_value=self.item.type,
                options=SSHKeyTypeOptions,
                label="Type",
            ),
            rio.NumberInput(
                on_change=lambda e: setattr(self.item, "bits", int(e.value)),
                value=self.item.bits,
                label="Bits",
                decimals=0,
            ),
            min_width=30.0,
            spacing=1.0,
        )


class SSHPage(rio.Component):
    """A CRUD page that allows users to create, read, update, and delete menu
    items.

    The @rio.event.on_populate decorator is used to fetch data from a
    predefined data model and assign it to the menu_items attribute of
    the current instance.


    ## Attributes

    `banner_text`: The text to be displayed in the banner.

    `banner_style`: The style of the banner (success, danger, info).

    `currently_selected_menu_item`: The currently selected menu item.

    `menu_items`: A list of menu items.
    """

    banner_text: str = ""
    banner_style: Literal["success", "danger", "info"] = "success"
    currently_selected_menu_item: Optional[KeyItem] = None
    menu_items: List[KeyItem] = []

    @rio.event.on_populate
    def on_populate(self) -> None:
        """Event handler that is called when the component is populated.

        Fetches data from a predefined data model and assigns it to the
        menu_items attribute of the current instance.
        """
        account: Account = self.session[Account]
        setting: UserSettings = self.session[UserSettings]
        if profile := account.fetch(setting.session_id, setting.secret_key):
            for name in (ring := SSHKeyRing(base=profile.workspace)):
                self.menu_items.append(KeyItem.create(name, ring[name]))

    async def on_press_create_item(self) -> None:
        new_item: KeyItem = KeyItem.empty()

        def build_dialog_content() -> rio.Component:
            return rio.Column(
                AddKeyItemComponent(new_item),
                rio.Row(
                    rio.Button(
                        "Save",
                        color="keep",
                        style="major",
                        # on_press=lambda selected_menu_item_copied=selected_menu_item_copied: dialog.close(
                        #     selected_menu_item_copied
                        # ),
                    ),
                    rio.Button(
                        "Cancel",
                        color="danger",
                        style="minor",
                        on_press=lambda: dialog.close(None),
                    ),
                    spacing=1.0,
                ),
                spacing=1.0,
            )

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
        try:
            file = self.session.pick_file(multiple=False)
            await file
        except rio.NoFileSelectedError:
            pass

    async def on_press_delete_item(self, name: str) -> None:
        """Perform actions when the "Delete" button is pressed."""
        # delete the item from the list
        # self.menu_items.pop(index)
        account: Account = self.session[Account]
        setting: UserSettings = self.session[UserSettings]
        if profile := account.fetch(setting.session_id, setting.secret_key):
            ring: SSHKeyRing = SSHKeyRing(base=profile.workspace)
            if ring.remove(name):
                self.banner_text = f"Successfully deleted {name}"
                self.banner_style = "success"
                self.force_refresh()
            else:
                self.banner_text = f"Failed to delete {name}"
                self.banner_style = "danger"

    def build(self) -> rio.Component:
        """Builds the component to be rendered."""

        # Then unpack the list to pass the children to the ListView
        return rio.Column(
            Navbar(
                rio.Button(
                    content="Create",
                    icon="material/add",
                    color="success",
                    shape="rounded",
                    style="minor",
                    on_press=self.on_press_create_item,
                ),
                rio.Button(
                    content="Upload",
                    icon="material/upload",
                    color="secondary",
                    shape="rounded",
                    style="minor",
                    on_press=self.on_press_upload_item,
                ),
            ),
            rio.Column(
                rio.Text(text="SSH keys", style="heading2"),
                rio.Banner(self.banner_text, style=self.banner_style),
                *[
                    KeyItemComponent(
                        item=item,
                        on_delete=functools.partial(
                            self.on_press_delete_item, item.name
                        ),
                    )
                    for item in self.menu_items
                ],
                # align at the top
                align_y=0.0,
                grow_y=True,
                spacing=1.0,
                margin_x=3.0,
            ),
        )
