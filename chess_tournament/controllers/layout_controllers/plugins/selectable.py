import abc

from chess_tournament.controllers.layout_controller import LayoutController


class SelectablePlugin(abc.ABC):
    def __init__(
            self,
            detail_selection_LC: LayoutController = None,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.detail_selection_LC = detail_selection_LC
        self.data = NotImplementedError
        self.selectables = NotImplementedError
        self.index = -1
        self.multiple_selection = set()
        self.multiple_selection_color = 'yellow'
        # when single selected and multiple at the same time
        self.double_selection_color = 'green'
        self.single_selection_color = 'blue'

    def _move(self, increment):
        # reset previous row's color
        if self.index in self.multiple_selection:
            self.selectables[self.index].style = self.multiple_selection_color
        else:
            self.selectables[self.index].style = None

        # update index
        self.index += increment
        len_table = len(self.selectables)
        if self.index < 0:
            self.index = len_table - 1
        elif self.index >= len_table:
            self.index = 0

        # set current row's color
        if self.index in self.multiple_selection:
            self.selectables[self.index].style = self.double_selection_color
        else:
            self.selectables[self.index].style = self.single_selection_color

        lc = self.detail_selection_LC
        if lc is not None:
            lc.data = self.data[self.index]
            self.page.update_by_controller(lc)

    def up(self):
        '''Go to upper table row
        shortcut_name = Aller la ligne supérieure
        '''
        self._move(1)

    def down(self):
        '''Go to upper table row
        shortcut_name = Aller la ligne inférieure
        '''
        self._move(-1)

    def select(self):
        '''Select/unselect current row
        shortcut_name = (dé)sélectionner la ligne
        '''
        if self.index in self.multiple_selection:
            self.multiple_selection.remove(self.index)
        else:
            self.multiple_selection.add(self.index)
        self._move(0)

    def select_all(self):
        '''Select all row
        shortcut_name = Tout (dé)sélectionner
        '''
        if self.multiple_selection:
            self.multiple_selection = set()
        else:
            self.multiple_selection = set(range(len(self.data)))
            # self.multiple_selection = set(range(len(self.selectables)))
        self.page.update_by_controller(self)
        self._move(0)
