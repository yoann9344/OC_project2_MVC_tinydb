"""Module to start the program using MainController."""
from typing import Type

from rich.console import Console
from rich.live import Live

from .page import Page
from chess_tournament.views.view import LayoutView
from chess_tournament.tools.key import KBHit
from .pages import ExitPage,  WelcomPage

import logging

logging.basicConfig(filename='logs.log', level=logging.INFO)


class _Browser():
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
        """Go to the previous page visited.

        shortcut_name = Page précédente
        """
        self._check_index_value()
        if self.index == 0:
            return

        self.index -= 1
        self._move()

    def go_foreward(self):
        """Go to the next page visited.

        shortcut_name = Page suivante
        """
        self._check_index_value()
        if self.index == len(self.history) - 1:
            return

        self.index += 1
        self._move()


class MainController(_Browser):
    """Main program, controlling everything, start it with loop()."""

    def __init__(self):
        self.console = Console()
        self.log = self.console.log
        layout = LayoutView()
        self.layout_view = layout

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
            'M': self.go_to_menu,
        }
        Page.loop = self
        self.menu = WelcomPage()
        super().__init__(self.menu)
        self.edition_mode = False
        self.buffer = ''
        self.edition_callback = None

    def go_to_menu(self):
        """Go back to the menu.

        shortcut_name = Retourner au menu principal
        """
        self.go_to(self.menu)

    def quit_dialog(self):
        """Open quit dialog.

        shortcut_name = Quitter
        """
        self._page = ExitPage()
        self.need_update = True

    def handle_keyboard(self):
        """Handle shortcuts and edition mode's buffer."""
        entries = self.kb.read()
        codes = [ord(c) for c in entries]

        if self.edition_mode:
            if 27 in codes:
                self.stop_edition_mode()
                return
            entries = ''
            for c in codes:
                if c == 127:
                    # entries += '\b'
                    if len(entries):
                        entries = entries[:-1]
                    elif len(self.buffer):
                        self.buffer = self.buffer[:-1]
                elif c == 10:
                    entries += '\n'
                elif 32 <= c <= 126 or 161 <= c <= 255:
                    entries += chr(c)
                else:
                    entries += str(c)
            self.buffer += entries
            self.edition_callback(self.buffer, entries)
            return

        elif codes:
            self._page.codes = codes

            for code, func in (self.shortcuts | self.shortcuts_global).items():
                if isinstance(code, str):
                    code = ord(code)
                if code in codes:
                    func()

    def start_edition_mode(self, callback):
        """Handle edition mode, to desactivate shortcuts and crite text."""
        self.edition_mode = True
        self.edition_callback = callback

    def stop_edition_mode(self, force_stop=False):
        """Stop the edition mode. Reactivate shortcuts."""
        if not force_stop:
            self.edition_callback(self.buffer, '', desactivated=True)
        self.edition_mode = False
        self.edition_callback = None
        self.buffer = ''

    def loop(self):
        """Start main loop."""
        self.kb = KBHit()
        layout = self.layout_view.layout

        try:
            with Live(
                layout,
                refresh_per_second=10,
                screen=True,
                console=self.console,
            ) as live:
                while 1:
                    self.handle_keyboard()

                    if self.need_update:
                        self._page.update()
                        self.need_update = False
                    if self.exit_program:
                        break
                    live.update(layout)
        except Exception:
            self.console.print_exception(extra_lines=5, show_locals=True)
