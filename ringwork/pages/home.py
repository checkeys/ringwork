import rio


def guard(event: rio.GuardEvent) -> str | None:
    return


@rio.page(name="Home", url_segment="")
class InnerAppPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            # rio.PageView(
            #     grow_y=True,
            # ),
            rio.Markdown(
                """
# Buzzwordz Inc.!

Unleashing synergistic paradigms for unprecedented excellence since the day
after yesterday.
            """,
                min_width=60,
                align_x=0.5,
            ),
        )
