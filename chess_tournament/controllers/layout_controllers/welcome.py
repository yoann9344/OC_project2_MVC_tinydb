from types import MethodType

import inspect

from rich.layout import Layout
from rich.align import Align
from rich.panel import Panel
from rich.markdown import Markdown

from chess_tournament.models import mymodels
from chess_tournament.controllers.layout_controller import LayoutController


class WelcomeLayoutController(LayoutController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        welcome_message = inspect.cleandoc('''
            ## Bienvenu dans l'application de gestion de tournois d'échecs !
            - Pour créer une nouveau tournoi cliquez sur <T>.
            - Pour voir la liste des tournois cliquez sur <t>.
            - Pour voir la liste des joueurs cliquez sur <p>.
        ''')
        self.panel_view = Panel(
            Align.center(
                Markdown(welcome_message),
                vertical='middle'
            ),
            style='',
            title='',
            border_style=self.border_style,
        )

        self.shortcuts = {
            'T': self.new_tournament,
            't': self.show_tournaments,
            'p': self.show_players,
        }

    def update(self, layout: Layout):
        layout.update(self.panel_view)

    def new_tournament(self):
        """Go to page create tournament.

        shortcut_name = Créer un tournoi
        """
        from ..pages import TournamentCreatorPage

        self.page.loop.go_to(
            TournamentCreatorPage(
                loop=self.page.loop,
            )
        )

    def show_tournaments(self):
        """Go to page to show tournaments.

        shortcut_name = Liste des tournois
        """
        from ..pages import TablePage
        from ..layout_controllers import TableLayoutController

        def edit_tournament(self):
            """Edit the tournament.

            shortcut_name = Gérer le tournois.
            """
            from chess_tournament.controllers.pages import TournamentManagerPage
            if not self.multiple_selection and 0 <= self.index < len(self.data):
                self.page.loop.go_to(
                    TournamentManagerPage(
                        loop=self.page.loop,
                        tournament=self.data[self.index],
                    )
                )

        page = TablePage(
            loop=self.page.loop,
            model=mymodels.Tournament,
            headers=['id', 'name', 'place'],
        )
        controller: TableLayoutController = page.controllers['body']
        controller.edit_row = MethodType(edit_tournament, controller)
        controller.shortcuts['c'] = controller.edit_row
        # page.update_by_controller(controller)
        # page._change_focus()  # to update the new edit method
        self.page.loop.go_to(page)
        # controller.edit_row()

    def show_players(self):
        """Go to page to show players.

        shortcut_name = Liste des joueurs
        """
        from ..pages import TablePage
        self.page.loop.go_to(
            TablePage(
                loop=self.page.loop,
                model=mymodels.Player,
                headers=['id', 'name', 'firstname'],
            )
        )
