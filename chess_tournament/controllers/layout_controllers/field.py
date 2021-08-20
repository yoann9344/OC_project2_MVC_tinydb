from rich.layout import Layout

from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.views.table import TableView
from .plugins import SelectablePlugin


class FieldLayoutController(LayoutController, SelectablePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = (None, None, None)

        self.shortcuts = {
            'k': self.up,
            'j': self.down,
        }

    def update(self, layout: Layout):
        if self.index != -1:
            selection = self.index
        else:
            selection = None

        field, name, obj = self.data
        if field and name and obj:
            keys = obj._fields.keys()
            values = (str(getattr(self.row_object, k)) for k in keys)
            self.table = TableView(
                ['key', 'value'],
                list(zip(keys, values)),
                border_style=self.border_style,
                selection=selection
            )
            self.panel_view = self.table
            layout.update(self.table)
