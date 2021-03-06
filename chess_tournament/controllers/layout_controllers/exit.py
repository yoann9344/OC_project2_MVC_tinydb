from rich.layout import Layout
from rich.align import Align
from rich.panel import Panel

from chess_tournament.controllers.layout_controller import LayoutController


class ExitLayoutController(LayoutController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        yes_key = 'y'
        no_key = 'n'
        self.panel_view = Panel(
            Align.center(
                '[red]Quitter le programme ?[/red] '
                f'Oui <{yes_key}> Non <{no_key}>',
                vertical='middle'
            ),
            style='',
            title='',
            border_style=self.border_style,
        )
        self.loop = self.page.loop

        self.shortcuts = {
            yes_key: self.stop,
            no_key: self.resume,
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
