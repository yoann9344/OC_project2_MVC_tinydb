import copy
import time

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty

from tools.key import KBHit


class Placeholder:
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        self.panel = Panel(
            Align.center(Pretty('Blabla content'), vertical='middle'),
            style=self.style,
            title=self.highlighter(self.title),
            border_style='blue',
        )
        yield self.panel
        # yield table


class View():
    def __init__(self):
        # table = Table()
        # table.add_column('Player ID')
        # table.add_column('Rank')
        # table.add_column('Level')

        layout = Layout()
        self.layout = layout

        # Divide the 'screen' in to three parts
        layout.split(
            Layout(name='header', size=3),
            Layout(ratio=1, name='main'),
            Layout(size=10, name='footer'),
        )
        # Divide the 'main' layout in to 'side' and 'body'
        layout['main'].split_row(
            Layout(name='side'),
            Layout(name='body', ratio=2),
        )
        # Divide the 'side' layout in to two
        layout['side'].split(Layout(name='info'), Layout(name='dialog'))

        self.header = layout['header']
        main = layout['main']
        self.footer = layout['footer']

        side = main['side']
        self.body = main['body']

        self.info = side['info']
        self.dialog = side['dialog']

        self.footer._renderable = Placeholder('Super Titre')

        self.line = 'PLOP'

    def loop(self):
        footer = self.layout['footer']
        kb = KBHit()
        t = time.time()
        last_codes = None
        with Live(self.layout, refresh_per_second=4, screen=True):  # as live:
            while 1:
                entries = kb.read()
                codes = [ord(c) for c in entries]
                if len(entries) == 1 and last_codes == codes == [27]:
                    break
                # elif len(entries) == 3:
                #     self.line = str(codes)
                #     # self.line = '3PLOP'
                #     if codes == [27, 91, 68]:
                #         self.line = 'You hit the left key!'
                #     elif codes == [27, 91, 67]:
                #         self.line = 'You hit the right key!'
                elif len(entries) > 0:
                    # self.line += str(len(entries))
                    self.line = str(codes) + str(last_codes)
                    # self.line += entries
                if codes:
                    last_codes = copy.deepcopy(codes)
                footer.update(
                    Panel(
                        Align.center(Pretty('Blabla'), vertical='middle'),
                        style='',
                        title=self.line,
                        border_style='blue',
                    )
                )
                if 6 > time.time() - t > 4:
                    self.line = 'Changed'
                time.sleep(0.1)
