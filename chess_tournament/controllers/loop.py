import copy
import time

import rich
from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.prompt import Prompt

from chess_tournament.models.test import Player
from chess_tournament.views.view import LayoutView
from chess_tournament.views.table import TableView
from chess_tournament.tools.key import KBHit

import logging

logging.basicConfig(filename='logs.log', level=logging.INFO)


class Browser():
    def __init__(self, Controller):
        self.history = [{
            'cls': Controller,
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
        # self._controller.on_page_change()
        target = self.history[self.index]
        controller = target['cls'](self, **target['kwargs'])
        self._controller = controller
        self.need_update = True

    def go_to(self, Controller, **kwargs):
        self._check_index_value()
        len_history = len(self.history)
        current = self.history[self.index]
        if Controller == current:
            current['kwargs'] = kwargs
        else:
            if self.index < len_history - 1:
                self.history = self.history[:self.index+1]
            self.history.append({
                'cls': Controller,
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


class Controller():
    def __init__(self, loop: 'MainController'):
        self.loop = loop
        self.shortcuts = {}


class TableController(Controller):
    pass


class Page():
    def __init__(self, loop):
        self.controllers = {
            'header': None,
            'footer': None,
            'body': None,
            'info': None,
            'dialog': None,
        }
        self._focus = 'body'
        self.loop = loop

        # always give shortcuts info
        self.codes = []
        self.align = Align.center('', vertical='middle')
        self.footer = Panel(
            self.align,
            style='',
            title='Commandes',
            border_style='blue',
        )

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, value: str):
        if value not in self.controllers:
            return
        self._focus = value
        # for specific behaavior overide change_focus not focus
        self.change_focus()

    def change_focus(self):
        controller: Controller = self.controllers.get(self._focus, None)
        if controller is not None:
            self.loop.shortcuts = controller.shortcuts

    @property
    def codes(self):
        return self._codes

    @codes.setter
    def codes(self, codes):
        self._codes = codes
        if codes and 33 <= codes[0] <= 126:
            self.align.renderable = 'Key pressed : {}'.format(chr(codes[0]))


class TablePage(Page):
    def update(self):
        self.loop.footer.update(self.footer)
        self.index = -1
        self.data = Player.all()
        self.table = TableView(
            ['id', 'rank'],
            self.data,
        )
        self.loop.body.update(self.table)

        self.loop.shortcuts = {
            'k': self.up,
            'j': self.down,
        }

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

        self._show_info()

    def _show_info(self):
        row_object: Player = self.data[self.index]
        keys = row_object._fields.keys()
        values = (getattr(row_object, k) for k in keys)
        self.table_info = TableView(
            ['key', 'value'],
            list(zip(keys, values)),
        )
        self.loop.info.update(self.table_info)

    def up(self):
        self._move(1)

    def down(self):
        self._move(-1)

        # for name, renderable in self.layouts_to_update.items():
        #     # layout = getattr(self.loop, name)
        #     # print(name, layout)
        #     # layout.update(renderable)


class ExitController(Controller):
    def update(self):
        # self.render()
        # self.panel.safe_box
        self.panel = Panel(
            Align.center(
                '[red]Quitter le programme ? []Oui <o> Non <n>',
                vertical='middle'
            ),
            style='',
            title='',
            border_style='blue',
        )
        self.loop.body.update(self.panel)
        self.loop.footer.update(self.footer)

        self.loop.shortcuts = {
            'o': self.stop,
            'n': self.resume,
        }

    def stop(self):
        self.loop.exit_program = True

    def resume(self):
        self.loop.shortcuts = {}
        self.loop._move()


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
        super().__init__(WelcomeController)
        self.go_to(WelcomeController)

    def handle_shortcuts(self):
        entries = self.kb.read()
        codes = [ord(c) for c in entries]
        # if len(entries) == 1 and self.last_codes == codes == [27]:
        if codes == [ord('q')]:
            self._controller = ExitController(self)
            self.need_update = True

        # self._controller.update(codes)
        if codes:
            self.last_codes = copy.deepcopy(codes)
            self._controller.codes = codes
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
                    self._controller.update()
                    self.need_update = False

                if self.exit_program:
                    break
                rich.print(layout.layout)
                time.sleep(0.1)
        except Exception:
            self.console.print_exception(extra_lines=5, show_locals=True)
