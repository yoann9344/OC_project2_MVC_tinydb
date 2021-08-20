from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    TournamentManagerLayoutController,
)
from chess_tournament.models import mymodels


class TournamentPage(Page):
    def init_controllers(
        self,
        tournament: mymodels.Tournament,
        *args,
        **kwargs
    ):
        # tree = TournamentTreeLayoutController(page=self)
        # scores = ScoresLayoutController(page=self)
        manager = TournamentManagerLayoutController(tournament, page=self)
        self.controllers.update({
            'body': manager,
            # 'info': tree,
        })
        self.focus = 'body'
