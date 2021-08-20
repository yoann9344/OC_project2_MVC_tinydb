from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from rich.panel import Panel

from .layout_controller import LayoutController
from .layout_controllers import ShortcutsLayoutController

if TYPE_CHECKING:
    from . import MainController


class Page(ABC):
    loop: 'MainController' = None

    def __init__(self, *args, **kwargs):
        self.controllers = {
            'header': None,
            'footer': None,
            'body': None,
            'info': None,
            'dialog': None,
        }
        self._focus = 'body'
        self._focus_controller = None
        self.border_style = 'blue'
        self.empty_layout = Panel(
            '',
            style='',
            title='',
            border_style=self.border_style,
        )

        # any page gives shortcuts info
        self.controllers['footer'] = ShortcutsLayoutController(
            self.loop.shortcuts_global,
            page=self,
        )

        self.init_controllers(*args, **kwargs)

    def update(self):
        for layout_name, controller in self.controllers.items():
            if controller is None:
                getattr(self.loop, layout_name).update(self.empty_layout)
            else:
                controller.update(getattr(self.loop, layout_name))

    def update_by_name(self, name):
        controller = self.controllers.get(name, None)
        layout = getattr(self.loop, name, None)
        if controller is not None and layout is not None:
            controller.update(layout)

    def update_by_controller(self, controller):
        for layout_name, c in self.controllers.items():
            if id(c) == id(controller):
                controller.update(getattr(self.loop, layout_name))

    def replace_controller(self, current, *, replaced_by):
        for layout_name, c in self.controllers.items():
            if id(c) == id(current):
                self.controllers[layout_name] = replaced_by
                self._change_focus()
                replaced_by.update(getattr(self.loop, layout_name))

    @abstractmethod
    def init_controllers(self):
        pass

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, value: str):
        if value not in self.controllers:
            return
        if self._focus_controller is not None:
            self._focus_controller.set_border_style()
        self._focus = value
        self._change_focus()

    def focus_by_controller(self, controller):
        for layout_name, c in self.controllers.items():
            if id(c) == id(controller):
                self.focus = layout_name
                break

    def _change_focus(self):
        controller: LayoutController = self.controllers.get(self._focus, None)
        if controller is not None:
            self.loop.shortcuts = controller.shortcuts
            self._focus_controller = controller
            controller.set_border_style('green')
            self.controllers['footer'].show_shortcuts(controller.shortcuts)

    @property
    def codes(self):
        return self.controllers['footer'].codes

    @codes.setter
    def codes(self, codes):
        self.controllers['footer'].codes = codes
