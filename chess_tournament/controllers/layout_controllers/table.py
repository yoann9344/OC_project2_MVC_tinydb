import operator

from rich.layout import Layout

from chess_tournament import models
from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.controllers.layout_controllers import RowLayoutController
from chess_tournament.views.table import TableView


class TableLayoutController(LayoutController):
    def __init__(
        self,
        model: models.Model,
        headers: list[str] = None,
        shortcuts: dict = {},
        info_layout_controller: 'RowLayoutController' = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.info_layout_controller = info_layout_controller
        self.shortcuts = {
            'k': self.up,
            'j': self.down,
            't': self.sort,
            'T': self.reverse_sort,
        }
        self.index = -1
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

    def _move(self, increment):
        # reset previous row's color
        self.table.rows[self.index].style = None

        # update index
        self.index += increment
        len_table = len(self.table.rows)
        if self.index < 0:
            self.index = len_table - 1
        elif self.index >= len_table:
            self.index = 0

        # set current row's color
        self.table.rows[self.index].style = 'blue'

        lc = self.info_layout_controller
        if lc is not None:
            lc.row = self.data[self.index]
            self.page.update_by_controller(lc)

    def up(self):
        '''Select upper table row
        shortcut_name = Sélectionner la ligne supérieure
        '''
        self._move(1)

    def down(self):
        '''Select upper table row
        shortcut_name = Sélectionner la ligne inférieure
        '''
        self._move(-1)
