import copy
import inspect
import operator
import re
import time
from abc import ABC, abstractmethod
from typing import Type, Callable

import rich
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.pretty import Pretty
from rich.prompt import Prompt
from rich.table import Table

from chess_tournament import models
from chess_tournament.models.test import Player
from chess_tournament.views.view import LayoutView
from chess_tournament.views.table import TableView
from chess_tournament.tools.key import KBHit

import logging

logging.basicConfig(filename='logs.log', level=logging.INFO)


class Browser():
    def __init__(self, start_page: Type['Page']):
        self.history = [start_page]
        self.index = 0
        self.need_update = False
        self._move()

    def _check_index_value(self):
        len_history = len(self.history)
        if self.index >= len_history:
            self.index = len_history - 1
        elif self.index < 0:
            self.index = 0

    def _move(self):
        self._check_index_value()
        # self._page.on_page_change()
        self._page = self.history[self.index]
        self._page.focus = self._page.focus
        self.need_update = True

    def go_to(self, page: 'Page'):
        self._check_index_value()
        len_history = len(self.history)
        current = self.history[self.index]
        if id(page) == id(current):
            pass
        else:
            if self.index < len_history - 1:
                self.history = self.history[:self.index+1]
            self.history.append(page)
            self.index += 1
            self._move()

    def go_backward(self):
        '''Go to the previous page visited
        shortcut_name = Page précédente
        '''
        self._check_index_value()
        if self.index == 0:
            return

        self.index -= 1
        self._move()

    def go_foreward(self):
        '''Go to the next page visited
        shortcut_name = Page suivante
        '''
        self._check_index_value()
        if self.index == len(self.history) - 1:
            return

        self.index += 1
        self._move()


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


class RowLayoutController(LayoutController):
    def __init__(self, row: models.Model = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row = row

    def update(self, layout: Layout):
        if self.row is not None:
            row_object: models.Model = self.row
            keys = row_object._fields.keys()
            values = (getattr(row_object, k) for k in keys)
            self.table_info = TableView(
                ['key', 'value'],
                list(zip(keys, values)),
            )
            layout.update(self.table_info)


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


class TablePage(Page):
    def init_controllers(self, model: models.Model, *args, **kwargs):
        info = RowLayoutController()
        self.controllers.update({
            'body': TableLayoutController(
                model,
                info_layout_controller=info,
                page=self,
            ),
            'info': info,
        })
        self.focus = 'body'


class ExitLayoutController(LayoutController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.panel_view = Panel(
            Align.center(
                f'[red]Quitter le programme ?[/red] Oui <o> Non <n>{self.border_style}',
                vertical='middle'
            ),
            style='',
            title='',
            border_style=self.border_style,
        )
        self.loop = self.page.loop

        self.shortcuts = {
            'o': self.stop,
            'n': self.resume,
        }

    def stop(self):
        '''Stop send signal to stop the loop, then exit the program
        shortcut_name = Oui
        '''
        self.loop.exit_program = True

    def resume(self):
        '''Cancel stop
        shortcut_name = Non
        '''
        self.loop.shortcuts = {}
        self.loop._move()

    def update(self, layout: Layout):
        layout.update(self.panel_view)


class ExitPage(Page):
    def init_controllers(self, *args, **kwargs):
        self.controllers.update({
            'body': ExitLayoutController(page=self),
        })
        self.focus = 'body'


class MainController(Browser):
    def __init__(self):
        nb_players = len(Player.all())

        import string
        import random

        def name_generator():
            chars = chars = string.ascii_letters
            size = random.randint(3, 10)
            return ''.join(random.choice(chars) for _ in range(size))

        while nb_players < 10:
            Player(
                rank=random.randrange(10),
                name=name_generator()
            )
            nb_players += 1

        self.console = Console()
        self.log = self.console.log
        layout = LayoutView()
        self.layout = layout

        self.header = layout.header
        self.footer = layout.footer
        self.body = layout.body
        self.info = layout.info
        self.dialog = layout.dialog

        self.exit_program = False
        self.shortcuts = {}
        self.shortcuts_global = {
            'w': self.go_backward,
            'x': self.go_foreward,
            'q': self.quit_dialog,
        }
        super().__init__(TablePage(self, model=Player))

    def quit_dialog(self):
        '''Open quit dialog
        shortcut_name = Quitter
        '''
        self._page = ExitPage(self)
        self.need_update = True

    def handle_shortcuts(self):
        entries = self.kb.read()
        codes = [ord(c) for c in entries]

        if codes:
            self.last_codes = copy.deepcopy(codes)
            self._page.codes = codes

        for code, func in (self.shortcuts | self.shortcuts_global).items():
            if isinstance(code, str):
                code = ord(code)
            if code in codes:
                func()

    def loop(self):
        layout = self.layout
        self.kb = KBHit()
        self.last_codes = None
        # with Live(layout.layout, refresh_per_second=4, screen=True, console=self.console) as live:
        try:
            while 1:
                self.handle_shortcuts()

                if self.need_update:
                    self._page.update()
                    self.need_update = False

                if self.exit_program:
                    break
                rich.print(layout.layout)
                time.sleep(0.1)
        except Exception:
            self.console.print_exception(extra_lines=5, show_locals=True)
