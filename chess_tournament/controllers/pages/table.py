from chess_tournament.controllers.page import Page

from ..layout_controllers import RowLayoutController, TableLayoutController
from chess_tournament import models


class TablePage(Page):
    def init_controllers(
        self,
        model: models.Model,
        headers: list[str] = None,
        *args,
        **kwargs
    ):
        info = RowLayoutController(page=self)
        self.controllers.update({
            'body': TableLayoutController(
                model,
                detail_selection_LC=info,
                headers=headers,
                page=self,
            ),
            'info': info,
        })
        self.focus = 'body'
