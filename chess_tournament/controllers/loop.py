import copy
import time
from typing import Type

import rich
from rich.console import Console
# from rich.live import Live

from .page import Page
from chess_tournament.models.mymodels import Player, Tournament
from chess_tournament.views.view import LayoutView
from chess_tournament.tools.key import KBHit
from .pages import ExitPage, TablePage, WelcomPage

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


class MainController(Browser):
    def __init__(self):
        nb_players = len(Player.all())

        import string
        import random
        import datetime

        def name_generator():
            chars = chars = string.ascii_letters
            size = random.randint(3, 10)
            return ''.join(random.choice(chars) for _ in range(size))

        while nb_players < 4:
            Player(
                name=name_generator(),
                firstname=name_generator(),
                birth=datetime.date(1983, 1, 22),
                rank=random.randint(2400, 2800)
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
        # super().__init__(TablePage(self, model=Player))
        super().__init__(WelcomPage(self))

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
        # with Live(layout.layout, refresh_per_second=4,
        # screen=True, console=self.console) as live:
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
