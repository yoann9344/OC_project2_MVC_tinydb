from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    WelcomeLayoutController, TournamentCreatorLayoutController
)


class WelcomPage(Page):
    def init_controllers(self, *args, **kwargs):
        self.controllers.update({
            'body': WelcomeLayoutController(self),
        })
        self.focus = 'body'
