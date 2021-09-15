from rich.layout import Layout

from chess_tournament import models
from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.views.table import TableView
from .plugins import SelectablePlugin


class RowLayoutController(LayoutController, SelectablePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

        self.shortcuts = {
            'k': self.up,
            'j': self.down,
            'e': self.edit,
        }

    def update(self, layout: Layout):
        if self.index != -1:
            selection = self.index
        else:
            selection = None

        row_object: models.Model = self.data
        if row_object:
            keys = row_object._fields.keys()
            values = [str(getattr(row_object, k)) for k in keys]
            self.table = TableView(
                ['key', 'value'],
                list(zip(keys, values)),
                border_style=self.border_style,
                selection=selection
            )
            self.selectables = self.table.rows
            self.panel_view = self.table
            layout.update(self.table)

    def edit(self):
        '''Edit the current field
        shortcut_name = Modifier
        '''
        if self.index != -1:
            selection = self.index
        else:
            selection = None

        if selection is not None:
            self.detail_selection_LC.take_focus_from(self)
