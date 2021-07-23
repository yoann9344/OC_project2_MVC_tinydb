import inspect
import re
from typing import Callable

from rich.layout import Layout
from rich.align import Align
from rich.panel import Panel
from rich.columns import Columns

from chess_tournament.controllers.layout_controller import LayoutController


class ShortcutsLayoutController(LayoutController):
    def __init__(self, shortcuts_global: dict[str, Callable], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._codes = []
        self.current_key = None
        self._shortcuts = {}
        self.shortcuts_global = shortcuts_global
        self.keys = list(
            self._shortcuts.keys() | self.shortcuts_global.keys()
        )
        self.align = Align.center('', vertical='middle')
        self.update_table()
        self.panel = Panel(
            self.align,
            style='',
            title='Commandes',
            border_style='blue',
        )

    def update(self, layout: Layout):
        self.update_table()
        layout.update(self.panel)

    def update_table(self):
        shortcuts = self.formatted_shortcuts()
        key = self.current_key
        # color last pressed key
        if key is not None:
            for i, value in enumerate(shortcuts):
                if f'<{key}>' in value:
                    shortcuts[i] = value.replace(
                        f'<{key}>', f'<[blue]{key}[/blue]>'
                    )
        self.columns = Columns(
            shortcuts,
            equal=True,
            expand=True,
        )
        self.align.renderable = self.columns

    def formatted_shortcuts(self):
        result = []
        re_title = re.compile(r'shortcut_name *= *(.*)$')
        for name, func in (self._shortcuts | self.shortcuts_global).items():
            doc = inspect.getdoc(func)
            try:
                title = re.search(re_title, doc).group(1)
            except TypeError:
                raise TypeError(
                    f'Shortcut function "{func.__name__}" does not have '
                    'a docstring containing shortcut_name'
                )
            result.append('<{}> {}'.format(name, title))
        self.formatted = result
        return result

    @property
    def codes(self):
        return self._codes

    @codes.setter
    def codes(self, codes):
        self._codes = codes
        if codes and 33 <= codes[0] <= 126:
            char = chr(codes[0])
            if char in self.keys:
                self.current_key = char
                self.page.update_by_controller(self)

    @property
    def shortcuts(self):
        return self._shortcuts

    @shortcuts.setter
    def shortcuts(self, value: dict[str, Callable]):
        self._shortcuts = value
        self.keys = list(
            self._shortcuts.keys() | self.shortcuts_global.keys()
        )
        self.update_table()
        self.align.renderable = self.columns
