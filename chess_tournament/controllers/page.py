from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .layout_controller import LayoutController
from .layout_controllers import ShortcutsLayoutController

if TYPE_CHECKING:
    from . import MainController


class Page(ABC):
    def __init__(self, loop: 'MainController', *args, **kwargs):
        self.controllers = {
            'header': None,
            'footer': None,
            'body': None,
            'info': None,
            'dialog': None,
        }
        self._focus = 'body'
        self._focus_controller = None
        self.loop = loop

        # any page gives shortcuts info
        self.controllers['footer'] = ShortcutsLayoutController(
            loop.shortcuts_global,
            page=self,
        )

        self.init_controllers(*args, **kwargs)

    def update(self):
        for layout_name, controller in self.controllers.items():
            if controller is not None:
                controller.update(getattr(self.loop, layout_name))

    def update_by_name(self, name):
        controller = getattr(self, name, None)
        if controller is not None:
            controller.update(getattr(self.loop, name))

    def update_by_controller(self, controller):
        for layout_name, c in self.controllers.items():
            if id(c) == id(controller):
                controller.update(getattr(self.loop, layout_name))

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
        # for specific behavior overide change_focus not focus
        self._change_focus()

    def _change_focus(self):
        controller: LayoutController = self.controllers.get(self._focus, None)
        if controller is not None:
            self.loop.shortcuts = controller.shortcuts
            self._focus_controller = controller
            controller.set_border_style('green')
            self.controllers['footer'].shortcuts = controller.shortcuts

    @property
    def codes(self):
        return self.controllers['footer'].codes

    @codes.setter
    def codes(self, codes):
        self.controllers['footer'].codes = codes
