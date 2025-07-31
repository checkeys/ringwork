import rio


def guard(event: rio.GuardEvent) -> str | None:
    return
    # This website allows access to sensitive information. Enforce stringent
    # access control to all in-app pages.

    # Check if the user is authenticated by looking for a user session
    try:
        event.session[data_models.AppUser]

    except KeyError:
        # User is not logged in, redirect to the login page
        return "/"

    # User is logged in, no redirection needed
    return None


@rio.page(name="App", url_segment="")
class InnerAppPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            # Add some empty space so the navbar doesn't cover the content.
            # rio.Spacer(min_height=5.0, grow_y=True),
            rio.PageView(
                grow_y=True,
            ),
        )
