from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    PlayerCreatorLayoutController,
)


class PlayerCreatorPage(Page):
    def init_controllers(
        self,
        *args,
        **kwargs
    ):
        creator = PlayerCreatorLayoutController(page=self)
        self.controllers.update({
            'body': creator,
        })
        self.focus = 'body'
