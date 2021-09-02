from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    TournamentManagerLayoutController,
)
from chess_tournament.models import mymodels


class TournamentManagerPage(Page):
    def init_controllers(
        self,
        tournament: mymodels.Tournament,
        *args,
        **kwargs
    ):
        manager = TournamentManagerLayoutController(tournament, page=self)
        self.controllers.update({
            'body': manager,
        })
        self.focus = 'body'
