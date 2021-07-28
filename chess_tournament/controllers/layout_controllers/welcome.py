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
        '''Go to page create tournament
        shortcut_name = Créer un tournoi
        '''
        pass

    def show_tournaments(self):
        '''Go to page to show tournaments
        shortcut_name = Liste des tournois
        '''
        from ..pages import TablePage
        self.page.loop.go_to(
            TablePage(
                loop=self.page.loop,
                model=mymodels.Tournament,
                headers=['id', 'name', 'place'],
            )
        )

    def show_players(self):
        '''Go to page to show players
        shortcut_name = Liste des joueurs
        '''
        from ..pages import TablePage
        self.page.loop.go_to(
            TablePage(
                loop=self.page.loop,
                model=mymodels.Player,
                headers=['id', 'name', 'firstname'],
            )
        )
