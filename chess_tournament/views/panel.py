from rich.panel import Panel
from rich.align import Align
from rich.pretty import Pretty


class TextView(Panel):
    def __init__(self, content, title='', border_color='blue'):
        self.renderable = Align.center(
            Pretty(content),
            vertical='middle'
        ),
        self.style = self.style,
        self.title = title,
        self.border_style = 'blue',
