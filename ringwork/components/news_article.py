import rio


class NewsArticle(rio.Component):
    """
    Displays a news article with some visual separation from the background.
    """

    markdown: str

    def build(self) -> rio.Component:
        return rio.Card(
            rio.Markdown(
                self.markdown,
                margin=2,
            )
        )
