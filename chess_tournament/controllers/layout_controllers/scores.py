import collections
from operator import attrgetter

from chess_tournament.models import mymodels
from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.controllers.layout_controllers import TableLayoutController
from chess_tournament.views.table import TableView, CustomRow


class Score(CustomRow):
    def __init__(self, player_id, score):
        self.player_id = player_id
        self.player: str = mymodels.Player.get(doc_id=player_id).name
        self.score = score
        self.classement = 0

    @staticmethod
    def create_classement(scores: list['Score'], sort_it=False):
        if sort_it:
            scores.sort(key=attrgetter('score'), reverse=True)
        else:
            scores = sorted(scores, key=attrgetter('score'), reverse=True)
        previous = scores[0]
        previous.classement = 1
        for index, score in enumerate(scores):
            if previous.score == score.score:
                score.classement = previous.classement
            else:
                score.classement = index + 1


class ScoresLayoutController(TableLayoutController):
    def __init__(
        self,
        rounds: list[mymodels.Round],
        *args,
        **kwargs,
    ):
        super(LayoutController, self).__init__(*args, **kwargs)
        self.shortcuts = {
            # 'k': self.up,
            # 'j': self.down,
            's': self.sort,
            'S': self.reverse_sort,
            '/': self.start_filtering,
        }
        self.rounds = rounds
        scores = collections.Counter()
        for round_ in rounds:
            scores.update(round_.get_players_score())

        scores_objects: list[Score] = []
        for player_id, score in scores.most_common():
            scores_objects.append(Score(player_id, score))

        Score.create_classement(scores_objects, sort_it=True)
        self.title = 'Tableau des scores'

        self.model = Score
        self.headers = ['classement', 'player', 'score']
        self.sort_by = self.headers[0]
        self.sort_index = 0
        self.sort_reversed = False
        self.data: list[Score] = scores_objects
        self.table = TableView(
            self.headers,
            self.data,
            title=self.title,
            border_style=self.border_style,
        )
        self.panel_view = self.table
        self.selectables = self.table.rows
        self.info = None

    def update(self, layout):
        scores = collections.Counter()
        for round_ in self.rounds:
            scores.update(round_.get_players_score())

        scores_objects: list[Score] = []
        for player_id, score in scores.most_common():
            scores_objects.append(Score(player_id, score))

        Score.create_classement(scores_objects)
        self.data: list[Score] = scores_objects

        super().update(layout)

    def update_score(
        self,
        player: int or mymodels.Player,
        new_score,
        increment=False,
    ):
        if isinstance(player, mymodels.Player):
            player_id = player.id
        else:
            player_id = player
        for s in self.data.scores:
            if s.player_id == player_id:
                if increment:
                    s.score += new_score
                else:
                    s.score = new_score
                break
