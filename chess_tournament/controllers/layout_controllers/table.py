import operator

from rich.layout import Layout

from chess_tournament import models
from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.views.table import TableView
from ..layout_controllers import RowLayoutController
from .plugins import SelectableLayoutController


class TableLayoutController(LayoutController, SelectableLayoutController):
    def __init__(
        self,
        model: models.Model,
        headers: list[str] = None,
        shortcuts: dict = {},
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.shortcuts = {
            'k': self.up,
            'j': self.down,
            's': self.sort,
            'S': self.reverse_sort,
            'd': self.delete_row,
            'e': self.edit_row,
        }
        self.model = model
        self.headers = headers or ['id'] + list(self.model._fields.keys())
        self.sort_by = self.headers[0]
        self.sort_index = 0
        self.sort_reversed = False
        self.data: list[models.Model] = self.model.all()
        self.table = TableView(
            self.headers,
            self.data,
            border_style=self.border_style,
        )
        self.panel_view = self.table

    def update(self, layout: Layout):
        current_row_id = None
        if self.index != -1:
            selection = self.index
            current_row_id = self.data[selection].id
        else:
            selection = None
        self.data: list[models.Model] = self.model.all()
        self.data.sort(
            key=operator.attrgetter(self.sort_by),
            reverse=self.sort_reversed,
        )
        if current_row_id is not None:
            self.index = [x.id for x in self.data].index(current_row_id)
            selection = self.index
        selection = self.index if self.index != -1 else None
        self.table = TableView(
            self.headers,
            self.data,
            selection=selection,
            border_style=self.border_style,
        )
        self.table.columns[self.sort_index].header_style = 'blue'
        layout.update(self.table)

    def edit_row(self):
        '''Delete selected row
        shortcut_name = Supprimer la ligne
        '''
        self.detail_selection_LC.take_focus_from(self)

    def delete_row(self):
        '''Delete selected row
        shortcut_name = Supprimer la ligne
        '''
        if 0 <= self.index < len(self.data):
            self.data[self.index].delete()
            self.data.pop(self.index)
            if len(self.data) == self.index != 0:
                self._move(-1)
            else:
                self._move(0)
            self.page.update_by_controller(self)

    def sort(self):
        '''Sort row by next column
        shortcut_name = Trier la table
        '''
        index = self.sort_index + 1
        if index >= len(self.headers):
            self.sort_index = 0
        else:
            self.sort_index = index
        self.sort_by = self.headers[self.sort_index]
        self.page.update_by_controller(self)

    def reverse_sort(self):
        '''Reverse the current order
        shortcut_name = Inverser le tri
        '''
        self.sort_reversed ^= True
        self.page.update_by_controller(self)
