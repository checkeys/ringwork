import copy
import dataclasses
import functools
from typing import List
from typing import Literal
from typing import Optional

import rio
from xpw import Account
from xpw_keys import SSHKeyPair
from xpw_keys import SSHKeyRing
from xpw_keys import SSHKeyType

from ringwork.components.navbar import Navbar
from ringwork.components.user import UserSettings


@dataclasses.dataclass
class MenuItem:
    """MenuItem data model.

    ## Attributes

    `name`: The name of the menu item.

    `description`: The description of the menu item.
    """

    fingerprint: str
    comment: str
    private: str
    public: str
    type: SSHKeyType
    bits: int
    name: str

    def copy(self) -> "MenuItem":
        """Creates a copy of the MenuItem object."""
        return copy.copy(self)

    @classmethod
    def empty(cls) -> "MenuItem":
        """Creates a new empty MenuItem object."""
        return cls(fingerprint="",
                   comment="",
                   private="",
                   public="",
                   type="rsa",
                   bits=4096,
                   name="")

    @classmethod
    def create(cls, name: str, pair: SSHKeyPair) -> "MenuItem":
        return cls(fingerprint=pair.fingerprint,
                   comment=pair.comment,
                   private=pair.private,
                   public=pair.public,
                   type=pair.type,
                   bits=pair.bits,
                   name=name)


class SelectListView(rio.Component):

    item: MenuItem

    def build(self) -> rio.Component:
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
                        style="plain",
                        min_size=3.0,
                    ),
                    rio.IconButton(
                        icon="material/content_copy",
                        on_press=lambda: self.session.set_clipboard(
                            self.item.private
                        ),
                        style="plain",
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
                        style="plain",
                        min_size=3.0,
                    ),
                    rio.IconButton(
                        icon="material/content_copy",
                        on_press=lambda: self.session.set_clipboard(
                            self.item.public
                        ),
                        style="plain",
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
    currently_selected_menu_item: Optional[MenuItem] = None
    menu_items: List[MenuItem] = []

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
                self.menu_items.append(MenuItem.create(name, ring[name]))

    async def on_press_delete_item(self, index: int) -> None:
        """
        Perform actions when the "Delete" button is pressed.

        ## Parameters

        `idx`: The index of the item to be deleted.
        """
        # delete the item from the list
        self.menu_items.pop(index)
        self.banner_style = "success"
        self.banner_text = "Item was deleted"
        self.currently_selected_menu_item = None

    # Helper function to create a dialog for editing a menu item
    async def _create_dialog_item_editor(self, selected_menu_item: MenuItem, new_entry: bool) -> Optional[MenuItem]:  # noqa:E501
        """
        Creates a dialog to edit or add a menu item.

        This method creates a dialog that allows the user to edit or add
        a menu item. The dialog contains input fields for the name,
        description, price, and category of the menu item. The user can
        save or cancel the changes.
        If the user saves the changes, the updated menu item is returned.
        If the user cancels the changes, the original menu item is returned.

        ## Parameters

        `selected_menu_item`: The selected menu item to be edited or added.

        `new_entry`: A boolean flag indicating if the menu item is a new entry.


        See the approx. layout below:

        ```
        ╔══════════════════════ Card ══════════════════════╗
        ║ ┏━━━━━━━━━━━━━━━━━━━━ Text ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Edit Menu Item | Add New Menu Item           ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━ TextInput ━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Name                                         ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━ TextInput ━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Description                                  ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━ NumberInput ━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Price                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━ Dropdown ━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Category                                     ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━━━ Row ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃   ┏━━━ Button ━━━┓        ┏━━━ Button ━━━┓   ┃ ║
        ║ ┃   ┃ Save         ┃        ┃ Cancel       ┃   ┃ ║
        ║ ┃   ┗━━━━━━━━━━━━━━┛        ┗━━━━━━━━━━━━━━┛   ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ╚══════════════════════════════════════════════════╝
        ```
        """
        # Make a copy of the selected menu item to avoid modifying the
        # original, which is returned if the user cancels the dialog.
        selected_menu_item_copied = selected_menu_item.copy()

        # This function will be called to create the dialog's content.
        # It builds up a UI using Rio components, just like a regular
        # `build` function would.
        def build_dialog_content() -> rio.Component:
            # Build the dialog
            if new_entry is False:
                text = "Edit Menu Item"
            else:
                text = "Add New Menu Item"

            return rio.Column(
                rio.Text(
                    text=text,
                    style="heading2",
                    margin_bottom=1,
                ),
                rio.TextInput(
                    selected_menu_item_copied.name,
                    is_sensitive=False,
                    label="Name",
                    # on_change=on_change_name,
                ),
                rio.TextInput(
                    selected_menu_item_copied.fingerprint,
                    is_sensitive=False,
                    label="Description",
                    # on_change=on_change_description,
                ),
                rio.TextInput(
                    selected_menu_item_copied.type,
                    is_sensitive=False,
                    label="type",
                ),
                # rio.NumberInput(
                #     selected_menu_item_copied.price,
                #     label="Price",
                #     suffix_text="$",
                #     on_change=on_change_price,
                # ),
                # rio.Dropdown(
                #     options=[
                #         "Burgers",
                #         "Desserts",
                #         "Drinks",
                #         "Salads",
                #         "Sides",
                #     ],
                #     label="Category",
                #     selected_value=selected_menu_item_copied.category,
                #     on_change=on_change_category,
                # ),
                rio.Row(
                    rio.Button(
                        "Save",
                        on_press=lambda selected_menu_item_copied=selected_menu_item_copied: dialog.close(
                            selected_menu_item_copied
                        ),
                    ),
                    rio.Button(
                        "Cancel",
                        on_press=lambda: dialog.close(None),
                        style="minor",
                        color="danger",
                    ),
                    spacing=1,
                    align_x=1,
                ),
                spacing=1,
                align_y=0,
                align_x=0.5,
            )

        def on_change_name(ev: rio.TextInputChangeEvent) -> None:
            """Changes the name of the currently selected menu item.
            And updates the name attribute of our data model.

            ## Parameters

            `ev`: The event object that contains the new name.
            """
            selected_menu_item_copied.name = ev.text

        def on_change_description(ev: rio.TextInputChangeEvent) -> None:
            """Changes the description of the currently selected menu item.
            And updates the description attribute of our data model.

            ## Parameters

            `ev`: The event object that contains the new description.
            """
            selected_menu_item_copied.fingerprint = ev.text

        # def on_change_price(ev: rio.NumberInputChangeEvent) -> None:
        #     """
        #     Changes the price of the currently selected menu item. And updates the
        #     price attribute of our data model.

        #     ## Parameters

        #     `ev`: The event object that contains the new price.
        #     """
        #     selected_menu_item_copied.price = ev.value

        # def on_change_category(ev: rio.DropdownChangeEvent) -> None:
        #     """
        #     Changes the category of the currently selected menu item. And updates
        #     the category attribute of our data model.

        #     ## Parameters

        #     `ev`: The event object that contains the new category.
        #     """
        #     selected_menu_item_copied.category = ev.value

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
        result = await dialog.wait_for_close()

        # Return the selected value
        return result

    async def on_spawn_dialog_edit_menu_item(self, selected_menu_item: MenuItem, idx: int) -> None:  # noqa:E501
        """
        Opens a dialog to edit the selected menu item.

        Updates the menu item at the given index if the user confirms the changes.

        ## Parameters

        `selected_menu_item`: The selected menu item to be edited.

        `idx`: The index of the selected menu item in the list of menu items.
        """
        assert selected_menu_item is not None
        result = await self._create_dialog_item_editor(
            selected_menu_item=selected_menu_item, new_entry=False
        )

        # Ensure the result is not None
        if result is None:
            self.banner_text = "Item was NOT updated"
            self.banner_style = "danger"
        else:
            # Update the menu item
            self.menu_items[idx] = result
            self.banner_text = "Item was updated"
            self.banner_style = "info"

    async def on_spawn_dialog_add_new_menu_item(self) -> None:
        """Perform actions when the "Add New" ListItem is pressed.

        This method creates a new empty menu item of models.MenuItems.
        It then opens a dialog for the user to enter the details of the
        new menu item. If the user confirms the addition and the new
        menu item is not empty, it appends the new menu item to the list
        of menu items and updates the banner text accordingly.

        If the user cancels the addition or the new menu item is empty,
        it updates the banner text to indicate that the item was not added.
        """
        new_menu_item = MenuItem.empty()
        result = await self._create_dialog_item_editor(
            selected_menu_item=new_menu_item, new_entry=True
        )

        # Ensure the result is not None
        if result is None:
            self.banner_text = "Item was NOT updated"
            self.banner_style = "danger"
        else:
            # Append the new menu item to our list of menu items only
            # if it is not empty
            if result != MenuItem.empty():
                self.menu_items.append(result)
                self.banner_text = "Item was added"
                self.banner_style = "success"
            else:
                self.banner_text = "Item was NOT added"
                self.banner_style = "danger"

    async def on_press_item(self, selected_menu_item: MenuItem) -> None:
        """Creates a dialog to display a menu item."""

        def build_dialog_content() -> rio.Component:
            return rio.Column(
                SelectListView(item=selected_menu_item),
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
        """Builds the component to be rendered.

        If there is no currently selected menu item, only the Banner and
        ItemList component is returned.

        When you click on a SimpleListItem, a custom Dialog appears, allowing
        you to edit the selected item. Similarly, clicking on the "Add new"
        SimpleListItem opens a custom Dialog for adding a new item.

        See the approx. layout below:

        ```
        ╔══════════════════════ Column ═══════════════════════╗
        ║                               ┏━━━ IconButton  ━━━┓ ║
        ║                               ┗━━━ New SSH key ━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━━ Banner ━━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ "" | Item was updated | Item was added          ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━ ListView ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ ┏━━━━━━━━━━━━━━━━━ HeadingListItem ━━━━━━━━━━━┓ ┃ ║
        ║ ┃ ┃ SSH keys                                    ┃ ┃ ║
        ║ ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃ ║
        ║ ┃ ┏━━━━━━━━━━━━━━━━━ SimpleListItem ━━━━━━━━━━━━┓ ┃ ║
        ║ ┃ ┃ ┏━ Icon ━┓ Add new                          ┃ ┃ ║
        ║ ┃ ┃ ┗━━━━━━━━┛ Description                      ┃ ┃ ║
        ║ ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃ ║
        ║ ┃ ┏━━━━━━━━━━━━━━━━━ SimpleListItem ━━━━━━━━━━━━┓ ┃ ║
        ║ ┃ ┃ ┏━ Icon ━┓ Item 1         ┏━ IconButton ━┓  ┃ ┃ ║
        ║ ┃ ┃ ┗━━━━━━━━┛ Fingerprint    ┗━━━ Delete ━━━┛  ┃ ┃ ║
        ║ ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃ ║
        ║ ┃ ┏━━━━━━━━━━━━━━━━━ SimpleListItem ━━━━━━━━━━━━┓ ┃ ║
        ║ ┃ ┃ ┏━ Icon ━┓ Item 2         ┏━ IconButton ━┓  ┃ ┃ ║
        ║ ┃ ┃ ┗━━━━━━━━┛ Fingerprint    ┗━━━ Delete ━━━┛  ┃ ┃ ║
        ║ ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃ ║
        ║ ┃ ...                                             ┃ ║
        ║ ┃ ┏━━━━━━━━━━━━━━━━━ SimpleListItem ━━━━━━━━━━━━┓ ┃ ║
        ║ ┃ ┃ ┏━ Icon ━┓ Item n         ┏━ IconButton ━┓  ┃ ┃ ║
        ║ ┃ ┃ ┗━━━━━━━━┛ Fingerprint    ┗━━━ Delete ━━━┛  ┃ ┃ ║
        ║ ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ╚═════════════════════════════════════════════════════╝
        ```
        """

        # Store all children in an intermediate list
        list_items: rio.ListView = rio.ListView(align_y=0)

        for i, item in enumerate(self.menu_items):
            list_items.add(
                rio.SimpleListItem(
                    text=item.name,
                    secondary_text=item.fingerprint,
                    # left_child=rio.Checkbox(on_change=None),
                    left_child=rio.Icon(
                        "material/key",
                        fill="success",
                        min_height=2.5,
                        min_width=2.5,
                    ),
                    right_child=rio.Tooltip(
                        anchor=rio.IconButton(
                            icon="material/delete",
                            color="danger",
                            style="minor",
                            min_size=2.5,
                            on_press=functools.partial(
                                self.on_press_delete_item, i
                            ),
                        ),
                        tip="Delete",
                    ),
                    # Use the name as the key to ensure that the list item
                    # is unique.
                    key=item.name,
                    # Note the use of functools.partial to pass the
                    # item to the event handler.
                    on_press=functools.partial(self.on_press_item, item),
                )
            )

        # Then unpack the list to pass the children to the ListView
        return rio.Column(
            Navbar(
                rio.Button(
                    content="New SSH key",
                    icon="material/add",
                    color="secondary",
                    shape="rounded",
                    style="major",
                    on_press=self.on_spawn_dialog_add_new_menu_item,
                ),
            ),
            rio.Column(
                rio.Text(text="SSH keys", style="heading2"),
                rio.Banner(self.banner_text, style=self.banner_style),
                list_items,
                # align at the top
                align_y=0.0,
                grow_y=True,
                spacing=1.0,
                margin_x=3.0,
            ),
        )
