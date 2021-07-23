from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from rich.layout import Layout

if TYPE_CHECKING:
    from . import Page


class LayoutController(ABC):
    border_style = 'blue'

    def __init__(self, page: 'Page', *args, **kwargs):
        self.page: Page = page
        self.controller_which_gave_focus = None
        self.shortcuts = {}
        self._focus_shortcuts = {'b'}

    @abstractmethod
    def update(self, layout: Layout):
        pass

    def set_border_style(self, value=None):
        self.border_style = value or LayoutController.border_style
        self.panel_view.border_style = self.border_style
        self.page.update_by_controller(self)

    def take_focus_from(self, controller: 'LayoutController'):
        self.controller_which_gave_focus = controller

        self.shortcuts.update({
            'b': self.back_to_controller,
        })
        self.page.focus_by_controller(self)

    def back_to_controller(self):
        '''Go back to the previous focus
        shortcut_name = Retourner au focus précédent
        '''
        for key in self._focus_shortcuts:
            self.shortcuts.pop(key, None)
        self.page.focus_by_controller(self.controller_which_gave_focus)
