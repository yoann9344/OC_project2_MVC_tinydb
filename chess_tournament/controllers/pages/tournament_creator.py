from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    TournamentCreatorLayoutController,
)
from chess_tournament.models import mymodels


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
