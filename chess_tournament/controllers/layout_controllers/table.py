import operator
from typing import Callable

from rich.layout import Layout

from chess_tournament import models
from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.views.table import TableView
from .plugins import SelectablePlugin, EditablePlugin


class TableLayoutController(LayoutController, SelectablePlugin, EditablePlugin):
    def __init__(
        self,
        model: models.Model,
        headers: list[str] = None,
        LC_callback_to_send_selection: Callable = None,
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
            'c': self.edit_row,
            'v': self.select,
            'V': self.select_all,
            '/': self.start_filtering,
        }
        if LC_callback_to_send_selection is not None:
            self.shortcuts['y'] = self.send_selected_items

        self.title = None
        self.model = model
        self.headers = headers or ['id'] + list(self.model._fields.keys())
        self.LC_callback_to_send_selection = LC_callback_to_send_selection
        self.sort_by = self.headers[0]
        self.sort_index = 0
        self.sort_reversed = False
        self.data: list[models.Model] = self.model.all()
        if self.data:
            self.index = 0
        self.table = TableView(
            self.headers,
            self.data,
            title=f'Table {model.__name__}',
            border_style=self.border_style,
        )
        self.panel_view = self.table
        self.selectables = self.table.rows
        self.info = None

    def update(self, layout: Layout):
        # current_row_id = None
        # if self.index != -1:
        #     selection = self.index
        #     current_row_id = self.data[selection].id
        # else:
        #     selection = None
        # self.data: list[models.Model] = self.model.all()
        # self.data.sort(
        #     key=operator.attrgetter(self.sort_by),
        #     reverse=self.sort_reversed,
        # )
        # if current_row_id is not None:
        #     self.index = [x.id for x in self.data].index(current_row_id)
        #     selection = self.index
        selection = self.index if self.index != -1 else None
        self.table = TableView(
            self.headers,
            self.data,
            selection=selection,
            title=self.title or f'Table {self.model.__name__}',
            border_style=self.border_style,
            multiple_selection=self.multiple_selection,
            info=self.info,
        )
        self.panel_view = self.table
        self.selectables = self.table.rows
        self.table.columns[self.sort_index].header_style = 'blue'
        layout.update(self.table)

    def edit_row(self):
        """Edit selected row.

        shortcut_name = Éditer la sélection
        """
        self.detail_selection_LC.take_focus_from(self)

    def delete_row(self):
        """Delete selected row.

        shortcut_name = Supprimer la sélection
        """
        if not self.multiple_selection:
            indexes = [self.index]
        else:
            indexes = self.multiple_selection
        for i in sorted(indexes, reverse=True):
            if 0 <= i < len(self.data):
                self.data[i].delete()
                self.data.pop(i)
        self.multiple_selection.clear()
        new_length = len(self.data)
        if new_length <= i != 0:
            self._move(new_length - 1)
        elif new_length == 0:
            self.index = -1
            # TODO clear detail_selection_LC
        else:
            self._move(0)
        self.page.update_by_controller(self)

    def send_selected_items(self):
        """Confirm the selection, only used with a callback.

        shortcut_name = Valider la sélection
        """
        selected_ids = {self.data[i].id for i in self.multiple_selection}
        self.info = self.LC_callback_to_send_selection(selected_ids)

    def start_filtering(self):
        """Launch edit mode to filter rows.

        shortcut_name = Filtrer
        """
        self._previous_filter = self.data
        self._previous_selection = self.index
        self._previous_multiple_selection = self.multiple_selection
        self._previous_selectables = self.selectables

        self.index = -1
        self.multiple_selection = set()
        # self.selectables = []
        self._move(0)

        self._all_data: list[models.Model] = self.model.all()
        self.activate_edition(self.filter_rows)

    def filter_rows(self, buffer, last_entries, desactivated, cancelled):
        current_field_name = self.headers[self.sort_index]
        self.info = '/' + buffer

        def filter_rows(obj):
            return buffer in str(getattr(obj, current_field_name))

        if buffer != '':
            self.data = list(filter(filter_rows, self._all_data))
        else:
            self.data = self._all_data

        if cancelled:
            self.data = self._previous_filter
            self.index = self._previous_selection
            self.multiple_selection = self._previous_multiple_selection
            self.selectables = self._previous_selectables
            # self.selectables = self.table.rows
            self._move(0)
            self.info = None

        self.page.update_by_controller(self)

    def _sort(self):
        selected_ids = {self.data[i].id for i in self.multiple_selection}
        current_row_id = None
        if 0 < self.index < len(self.data):
            selection = self.index
            current_row_id = self.data[selection].id
        else:
            selection = None
        # self.data: list[models.Model] = self.model.all()
        self.data.sort(
            key=operator.attrgetter(self.sort_by),
            reverse=self.sort_reversed,
        )
        if current_row_id is not None:
            self.index = [x.id for x in self.data].index(current_row_id)
            selection = self.index
        self.multiple_selection = {
            i for i, obj in enumerate(self.data)
            if obj.id in selected_ids
        }

    def sort(self):
        """Sort row by next column.

        shortcut_name = Trier la table
        """
        # self.handle_selection_before_sorting()
        index = self.sort_index + 1
        if index >= len(self.headers):
            self.sort_index = 0
        else:
            self.sort_index = index
        self.sort_by = self.headers[self.sort_index]
        self._sort()
        self.page.update_by_controller(self)

    def reverse_sort(self):
        """Reverse the current order.

        shortcut_name = Inverser le tri
        """
        self.sort_reversed ^= True
        self._sort()
        self.page.update_by_controller(self)
