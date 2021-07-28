from chess_tournament.controllers.page import Page

from ..layout_controllers import (
    RowLayoutController, TableLayoutController, FieldLayoutController,
)
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
        table = TableLayoutController(
            model,
            detail_selection_LC=info,
            headers=headers,
            page=self,
        )
        fields = FieldLayoutController(page=self)
        self.controllers.update({
            'body': table,
            'info': info,
            'dialog': fields,
        })
        self.focus = 'body'
