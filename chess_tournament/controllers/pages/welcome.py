from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    WelcomeLayoutController, TournamentCreatorLayoutController
)


class WelcomPage(Page):
    def init_controllers(self, *args, **kwargs):
        self.controllers.update({
            'body': TournamentCreatorLayoutController(self),
            'info': WelcomeLayoutController(self),
        })
        self.focus = 'body'
