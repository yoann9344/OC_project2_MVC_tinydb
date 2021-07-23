from chess_tournament.controllers.page import Page

from ..layout_controllers import ExitLayoutController


class ExitPage(Page):
    def init_controllers(self, *args, **kwargs):
        self.controllers.update({
            'body': ExitLayoutController(page=self),
        })
        self.focus = 'body'
