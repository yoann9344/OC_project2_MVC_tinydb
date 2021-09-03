from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    TournamentCreatorLayoutController,
)


class TournamentCreatorPage(Page):
    def init_controllers(
        self,
        *args,
        **kwargs
    ):
        creator = TournamentCreatorLayoutController(page=self)
        self.controllers.update({
            'body': creator,
        })
        self.focus = 'body'
