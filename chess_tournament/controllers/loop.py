import copy
import time
from abc import ABC, abstractmethod
from typing import Type

import rich
from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.pretty import Pretty
from rich.prompt import Prompt

from chess_tournament import models
from chess_tournament.models.test import Player
from chess_tournament.views.view import LayoutView
from chess_tournament.views.table import TableView
from chess_tournament.tools.key import KBHit

import logging

logging.basicConfig(filename='logs.log', level=logging.INFO)


class Browser():
    def __init__(self, page: Type['Page']):
        self.history = [{
            'cls': page,
            'kwargs': {},
        }]
        self.index = 0
        self.need_update = False

    def _check_index_value(self):
        len_history = len(self.history)
        if self.index >= len_history:
            self.index = len_history - 1
        elif self.index < 0:
            self.index = 0

    def _move(self):
        self._check_index_value()
        # self._page.on_page_change()
        target = self.history[self.index]
        page = target['cls'](self, **target['kwargs'])
        self._page = page
        self.need_update = True

    def go_to(self, page: Type['Page'], **kwargs):
        self._check_index_value()
        len_history = len(self.history)
        current = self.history[self.index]
        if page == current:
            current['kwargs'] = kwargs
        else:
            if self.index < len_history - 1:
                self.history = self.history[:self.index+1]
            self.history.append({
                'cls': page,
                'kwargs': kwargs
            })
            self.index += 1
            self._move()

    def go_backward(self):
        self._check_index_value()
        if self.index == 0:
            return

        self.index -= 1
        self._move()

    def go_foreward(self):
        self._check_index_value()
        if self.index == len(self.history) - 1:
            return

        self.index += 1
        self._move()


class LayoutController(ABC):
    @abstractmethod
    def update(self, layout: Layout):
        pass


class RowLayoutController(LayoutController):
    def __init__(self, row: models.Model = None):
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
            page: 'Page',
            model: models.Model,
            headers: list[str] = None,
            shortcuts: dict = {},
            info_layout_controller: 'RowLayoutController' = None,
    ):
        # super().__init__()
        self.page = page
        self.info_layout_controller = info_layout_controller
        self.shortcuts = {
            'k': self.up,
            'j': self.down,
        }
        self.index = -1
        self.model = model
        self.headers = headers or ['id'] + list(self.model._fields.keys())

    def update(self, layout: Layout):
        self.data: list[models.Model] = self.model.all()
        selection = self.index if self.index != -1 else None
        self.table = TableView(
            self.headers,
            self.data,
            selection=selection
        )
        layout.update(self.table)

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
            self.page.update()
        # self.info_layout_controller.l
        # self._show_info()

    def _show_info(self):
        row_object: 'Player' = self.data[self.index]
        keys = row_object._fields.keys(['id'] + list(self.model._fields.keys()))
        values = (getattr(row_object, k) for k in keys)
        self.table_info = TableView(
            ['key', 'value'],
            list(zip(keys, values)),
        )
        self.info_layout.update(self.table_info)

    def up(self):
        self._move(1)

    def down(self):
        self._move(-1)


class ShortcutsLayoutController(LayoutController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._codes = []
        self.align = Align.center('', vertical='middle')
        self.panel = Panel(
            self.align,
            style='',
            title='Commandes',
            border_style='blue',
        )

    def update(self, layout: Layout):
        layout.update(self.panel)

    @property
    def codes(self):
        return self._codes

    @codes.setter
    def codes(self, codes):
        self._codes = codes
        if codes and 33 <= codes[0] <= 126:
            self.align.renderable = 'Key pressed : {}'.format(chr(codes[0]))


class Page(ABC):
    def __init__(self, loop, *args, **kwargs):
        self.controllers = {
            'header': None,
            'footer': None,
            'body': None,
            'info': None,
            'dialog': None,
        }
        self._focus = 'body'
        self.loop = loop

        # any page gives shortcuts info
        self.controllers['footer'] = ShortcutsLayoutController()
        self.init_controllers(*args, **kwargs)

    def update(self):
        for layout_name, controller in self.controllers.items():
            if controller is not None:
                controller.update(getattr(self.loop, layout_name))

    def update_by_name(self, name):
        controller = getattr(self, name, None)
        if controller is not None:
            controller.update(getattr(self.loop, name))

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
        self._focus = value
        # for specific behavior overide change_focus not focus
        self._change_focus()

    def _change_focus(self):
        controller: LayoutController = self.controllers.get(self._focus, None)
        if controller is not None:
            self.loop.shortcuts = controller.shortcuts

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
                self, model, info_layout_controller=info
            ),
            'info': info,
        })
        self.focus = 'body'


class ExitLayoutController(LayoutController):
    def __init__(self, loop: 'MainController'):
        self.panel = Panel(
            Align.center(
                '[red]Quitter le programme ?[/red] Oui <o> Non <n>',
                vertical='middle'
            ),
            style='',
            title='',
            border_style='blue',
        )
        self.loop = loop

        self.shortcuts = {
            'o': self.stop,
            'n': self.resume,
        }

    def stop(self):
        self.loop.exit_program = True

    def resume(self):
        self.loop.shortcuts = {}
        self.loop._move()

    def update(self, layout: Layout):
        layout.update(self.panel)


class ExitPage(Page):
    def init_controllers(self, *args, **kwargs):
        self.controllers.update({
            'body': ExitLayoutController(self.loop),
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
        super().__init__(TablePage)
        self.go_to(TablePage, model=Player)

    def handle_shortcuts(self):
        entries = self.kb.read()
        codes = [ord(c) for c in entries]
        # if len(entries) == 1 and self.last_codes == codes == [27]:
        if codes == [ord('q')]:
            self._page = ExitPage(self)
            self.need_update = True

        # self._page.update(codes)
        if codes:
            self.last_codes = copy.deepcopy(codes)
            self._page.codes = codes
            # self.go_to(WelcomeController, codes=codes)

        for code, func in self.shortcuts.items():
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
