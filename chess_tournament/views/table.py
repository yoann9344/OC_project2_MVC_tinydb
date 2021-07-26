from rich.align import Align
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table

from chess_tournament.models import Model


class TableView(Panel):
    def __init__(self, headers: list[str], rows: list[dict] or list[Model], title=None, border_style='blue', selection=None):
        self.style = ''
        table = Table(style=self.style, title=title, border_style=None)
        for h in headers:
            table.add_column(h)
        for i, row in enumerate(rows):
            color = ''
            if i == selection:
                # color = '[blue]'
                color = 'blue'
            if isinstance(row, Model):
                table.add_row(
                    *[str(getattr(row, h, '')) for h in headers],
                    style=color
                )
            elif isinstance(row, dict):
                table.add_row(
                    *[str(row.get(h, '')) for h in headers],
                    style=color
                )
            elif isinstance(row, tuple):
                table.add_row(
                    *[row[j] for j in range(len(headers))],
                    style=color
                )
            else:
                table.add_row(
                    *[Pretty(row) for h in headers],
                    style=color
                )
        self.rows = table.rows
        self.columns = table.columns
        super().__init__(
            Align.center(
                table,
                vertical='top',
            ),
            style=self.style,
            title=title,
            border_style=border_style,
        )


if __name__ == '__main__':
    TableView(
        ['id', 'value'],
        [
            {'id': 1, 'value': 'plop'},
            {'id': 2, 'value': 'plop'},
            {'id': 3, 'value': 'plep'},
            {'id': 4, 'value': 'plzp'},
            {'id': 5, 'value': 'plap'},
        ]
    )
