from typing import Optional

import rio
from xpw import Account


def Restrict(event: rio.GuardEvent) -> Optional[str]:
    account: Account = event.session[Account]
    print(event.session.active_page_url.raw_parts)


@rio.page(name="Public", url_segment="pub", guard=Restrict)
class PublicPage(rio.Component):

    def build(self) -> rio.Component:
        account: Account = self.session[Account]
        return rio.Html(
            html="test",
        )
