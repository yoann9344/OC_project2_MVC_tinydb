import time

from rich.live import Live
from rich.table import Table

from .models.test import Player, Ref, Element
# from .views.views import ConsoleLayout


def run():
    # p1 = Player(rank=1)
    # p2 = Player(rank=2)
    # e1 = Element()
    # Ref(e=e1, p=p1)
    # return
    players = Player.all()
    # print('\n\n Well Done !!')
    # print(players)
    # print(players[0].ref)

    table = Table()
    table.add_column("Player ID")
    table.add_column("Rank")
    # table.add_column("Level")

    with Live(table, refresh_per_second=4) as live:  # update 4 times a second to feel fluid
        for player in players:
            live.console.print(f"Working on Player #{player.id}")
            time.sleep(0.4)
            table.add_row(f"{player.id}", f"{player.rank}")

    # class AsciiStdout(io.TextIOWrapper):
    #     pass

    # console = Console(
    #     file=(
    #         AsciiStdout(buffer=sys.stdout, encoding="ascii")
    #     ),
    #     theme=Theme(
    #         {"info": "dim cyan", "warning": "magenta", "danger": "bold red"}
    #     ),
    #     style='blue',
    #     force_terminal=True,
    #     force_interactive=True,
    # )
    # layout = ConsoleLayout(console)
    # layout.print('Message', 'code', 'stack trace', 'vars')
