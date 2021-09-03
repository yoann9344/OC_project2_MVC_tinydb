import collections
import inspect
import random
from operator import attrgetter

from rich.layout import Layout
from rich.align import Align
from rich.console import RenderGroup
from rich.panel import Panel
from rich.markdown import Markdown

from chess_tournament.models import mymodels
from chess_tournament.controllers.layout_controller import LayoutController
from ..layout_controllers import TableLayoutController
from ..layout_controllers.scores import ScoresLayoutController
from ..layout_controllers.round import RoundLayoutController


class TournamentManagerLayoutController(LayoutController):
    def __init__(self, tournament: mymodels.Tournament, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament

        self.shortcuts = {
        }

        self.description = inspect.cleandoc(f'''
            # {tournament.name}
            {tournament.description}
        ''')

        self.init_player_count()
        if self.nb_players < self.nb_players_required:
            self.shortcuts['i'] = self.popup_select_players_layout
            self.explainations = inspect.cleandoc(f'''
                **Vous devez inscrire au moins 4 joueurs** pour
                 débuter le tournois. Il manque {self.missing_players} joueurs.
                 Appuyer sur <i> pour ouvrir la page
                 de sélection. Puis naviguez avec <h> et <j> et sélectionnez
                 avec <v>. Une fois terminé validé avec <y>.

                NB -> vous pourrez effectuer :
                - une recherche avec '/' ;
                 <entrée> pour valider ; <echap> pour annuler
                - un tri par colonne ; <s> pour changer la colonne ;
                 <S> pour changer l'ordre (croissant, décroissant)
            ''')
        elif self.tournament.is_finished():
            self.explainations = inspect.cleandoc('''
                Le tournois est terminé !
            ''')
        elif len(tournament.rounds) == 0:
            self.explainations = inspect.cleandoc('''
                Le compte est bon ! Vous pouvez lancer le tirage au sort en
                appuyant sur <g>.
            ''')
        elif tournament.get_current_round is None:
            self.explainations = inspect.cleandoc('''
                Le tour est terminé.
                Appuyez sur <g> pour lancer le tirage au sort du prochain tour.
            ''')
        else:
            self.explainations = inspect.cleandoc('''
                Le tour n'est pas terminé.
                Certaines parties sont encore en cours.
            ''')

        self.groups = RenderGroup(
            Markdown(self.description),
            Markdown(self.explainations),
        )
        self.align = Align.center(
            self.groups,
            vertical='middle'
        )
        self.panel_view = Panel(
            self.align,
            style='',
            title=f'Gestion du tournois ({tournament.name})',
            border_style=self.border_style,
        )

    def init_player_count(self):
        self.nb_players_required = 4
        self.nb_players = len(self.tournament.players)
        self.missing_players = self.nb_players_required - self.nb_players

    def update(self, layout: Layout):
        self.groups = RenderGroup(
            Markdown(self.description),
            Markdown(self.explainations),
        )
        self.align = Align.center(
            self.groups,
            vertical='middle'
        )
        self.panel_view = Panel(
            self.align,
            style='',
            title=f'Gestion du tournois ({self.tournament.name})',
            border_style=self.border_style,
        )
        layout.update(self.panel_view)

    def popup_select_players_layout(self):
        """Show up a table to select players.

        shortcut_name = Sélectionner des joueurs
        """
        self.select_players_LC = TableLayoutController(
            mymodels.Player,
            LC_callback_to_send_selection=self.select_players_callback,
            page=self.page,
        )
        self.page.replace_controller(self, replaced_by=self.select_players_LC)

    def show_scores(self):
        self.page.controllers['dialog'] = ScoresLayoutController(
            self.tournament.rounds, page=self.page
        )
        self.page.update_by_name('dialog')

    def edit_rounds(self):
        """Give focus to rounds' controller.

        shortcut_name = 'Éditer les résultats des parties'
        """
        self.page.controllers['info'].take_focus_from(self)

    def show_current_round(self):
        current_round = self.tournament.get_current_round()
        if current_round is None:
            return

        self.page.controllers['info'] = RoundLayoutController(
            current_round, page=self.page
        )
        self.shortcuts['g'] = self.edit_rounds
        self.page.update()  # update 'info' and 'shortcuts'

    def get_focus_back(self):
        """Handle when get back focus."""
        if self.tournament.get_current_round() is None:
            self.shortcuts['g'] = self.generate_pairs
            if self.tournament.is_finished():
                self.explainations = inspect.cleandoc('''
                    Le tournois est terminé !
                ''')
            else:
                self.explainations = inspect.cleandoc('''
                    Le tour est terminé.
                    Appuyez sur <g> pour lancer le tirage au sort du prochain tour.
                ''')
            self.page.update_by_controller(self)

    def generate_pairs(self):
        """Generate pairs.

        shortcut_name = Générer les pairs
        """
        def generate_games(turn, players_sorted):
            nb_players = len(players_sorted)
            half = int(nb_players/2)
            for i, player_1 in enumerate(players_sorted[:half]):
                player_2 = players_sorted[i + half]
                white, black = random.sample([player_1, player_2], 2)
                mymodels.Game(white=white, black=black, turn=turn)

        tournament = self.tournament
        if tournament.get_current_round() is not None:
            return

        new_round = mymodels.Round(
            tournament=self.tournament,
            name=f'Round {len(tournament.rounds) + 1}',
        )
        if len(tournament.rounds) == 1:
            p_by_score_or_rank = sorted(
                tournament.players,
                key=attrgetter('rank'),
            )
        else:
            players_score = sum(
                (round_.get_players_score() for round_ in tournament.rounds),
                collections.Counter()
            )
            p_by_score_or_rank = sorted(
                tournament.players,
                key=lambda player: players_score[player.id],
            )
        generate_games(new_round, list(reversed(p_by_score_or_rank)))

        # pairs generated remove the shortcut
        self.shortcuts.pop('g')
        self.show_scores()
        self.show_current_round()
        self.edit_rounds()

    def select_players_callback(self, players_ids: set):
        if len(players_ids) > self.missing_players:
            return (
                'Trop de joueurs sélectionnés, il manque '
                f'{self.missing_players} joueurs pour commencer le tournois'
            )
        else:
            self.tournament.players.extend(players_ids)
            self.tournament.save()
            self.init_player_count()
            if self.missing_players == 0:
                self.explainations = inspect.cleandoc('''
                    Le compte est bon ! Vous pouvez lancer le tirage au sort en
                    appuyant sur <g>.
                ''')
                self.shortcuts.pop('i')
                self.shortcuts['g'] = self.generate_pairs
            else:
                self.explainations = inspect.cleandoc(f'''
                **Vous devez inscrire 4 joueurs** pour
                 débuter le tournois. Il manque {self.missing_players} joueurs.
                 Appuyer sur <i> pour ouvrir la page
                 de sélection. Puis naviguez avec <h> et <j> et sélectionnez
                 avec <v>. Une fois terminé validé avec <y>.

                NB -> vous pourrez effectuer :
                - une recherche avec '/' ;
                 <entrée> pour valider ; <echap> pour annuler
                - un tri par colonne ; <s> pour changer la colonne ;
                 <S> pour changer l'ordre (croissant, décroissant)
                ''')
            self.page.replace_controller(
                self.select_players_LC,
                replaced_by=self
            )
            self.select_players_LC = None
            self.page.update_by_controller(self)
