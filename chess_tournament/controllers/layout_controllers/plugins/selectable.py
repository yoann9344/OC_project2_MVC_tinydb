from chess_tournament.controllers.layout_controller import LayoutController


class SelectableLayoutController():
    def __init__(
            self,
            detail_selection_LC: LayoutController = None,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.detail_selection_LC = detail_selection_LC
        self.data = NotImplementedError
        self.index = -1

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

        lc = self.detail_selection_LC
        if lc is not None:
            lc.data = self.data[self.index]
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
