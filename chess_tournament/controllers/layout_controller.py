from abc import ABC, abstractmethod

from rich.layout import Layout


class LayoutController(ABC):
    border_style = 'blue'

    def __init__(self, page=None, *args, **kwargs):
        self.page = page

    @abstractmethod
    def update(self, layout: Layout):
        pass

    def set_border_style(self, value=None):
        self.border_style = value or LayoutController.border_style
        self.panel_view.border_style = self.border_style
