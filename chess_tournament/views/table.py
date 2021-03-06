from rich.align import Align
from rich.console import RenderGroup
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table

from chess_tournament.models import Model


class CustomRow():
    pass


class TableView(Panel):
    def __init__(
        self,
        headers: list[str],
        rows: list[dict] or list[Model],
        title=None,
        title_table=None,
        border_style='blue',
        selection=None,
        multiple_selection=[],
        multiple_selection_color='yellow',
        info=None,
    ):
        self.style = ''
        table = Table(style=self.style, title=title_table, border_style=None)
        for h in headers:
            table.add_column(h)
        for i, row in enumerate(rows):
            color = ''
            if i == selection:
                # color = '[blue]'
                color = 'blue'
            elif i in multiple_selection:
                color = multiple_selection_color
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
            elif isinstance(row, CustomRow):
                table.add_row(
                    *[str(getattr(row, h, '')) for h in headers],
                    style=color
                )
            else:
                table.add_row(
                    *[Pretty(row) for h in headers],
                    style=color
                )
        self.rows = table.rows
        self.columns = table.columns
        if info is not None:
            # renderable = RenderGroup(
            #     Align.center(
            #         table,
            #         vertical='top',
            #     ),
            #     Align.left(
            #         info,
            #         vertical='bottom',
            #     ),
            # )

            # renderable = RenderGroup(
            #     Align.center(
            #         table,
            #         vertical='top',
            #     ),
            #     Align.left(
            #         info,
            #         vertical='bottom',
            #     ),
            # )

            renderable = Align.center(
                RenderGroup(
                    table,
                    info,
                ),
                vertical='top',
            )
        else:
            renderable = Align.center(
                table,
                vertical='top',
            )

        super().__init__(
            renderable,
            style=self.style,
            title=title,
            border_style=border_style,
        )
