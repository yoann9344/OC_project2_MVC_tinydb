from rich.layout import Layout

from chess_tournament import models
from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.views.table import TableView


class RowLayoutController(LayoutController):
    def __init__(self, row: models.Model = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row = row

    def update(self, layout: Layout):
        if self.row is not None:
            row_object: models.Model = self.row
            keys = row_object._fields.keys()
            values = (getattr(row_object, k) for k in keys)
            self.table_info = TableView(
                ['key', 'value'],
                list(zip(keys, values)),
            )
            layout.update(self.table_info)
