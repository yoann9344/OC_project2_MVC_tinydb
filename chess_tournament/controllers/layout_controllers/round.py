from typing import TYPE_CHECKING

from chess_tournament.models import mymodels
from ..layout_controllers import TableLayoutController

if TYPE_CHECKING:
    from chess_tournament.models.mymodels import Round


class RoundLayoutController(TableLayoutController):
    def __init__(self, round_: 'Round', *args, scores_LC=None, **kwargs):
        self.round_ = round_
        self.data: list[mymodels.Game] = round_.games
        super().__init__(
            mymodels.Game,
            headers=['white', 'black', 'score'],
            *args,
            **kwargs,
        )
        self.shortcuts = {
            'k': self.up,
            'j': self.down,
            # 's': self.sort,
            # 'S': self.reverse_sort,
            '/': self.start_filtering,
            '1': self.white_won,
            '2': self.black_won,
            '3': self.equality,
            '0': self.game_not_finished,
        }
        self.data = round_.games
        self.scores_LC = scores_LC

    def white_won(self):
        '''Change game result, white won
        shortcut_name = Les blancs ont gagné
        '''
        if 0 <= self.index < len(self.data):
            game = self.data[self.index]
            game.white_won()
            game.save()
            self.page.update_by_controller(self)
            self.page.update()

    def black_won(self):
        '''Change game result, black won
        shortcut_name = Les noirs ont gagné
        '''
        if 0 <= self.index < len(self.data):
            game = self.data[self.index]
            game.black_won()
            game.save()
            self.page.update_by_controller(self)
            self.page.update()

    def equality(self):
        '''Change game result, equality
        shortcut_name = Match nul
        '''
        if 0 <= self.index < len(self.data):
            game = self.data[self.index]
            game.equality()
            game.save()
            self.page.update_by_controller(self)
            self.page.update()

    def game_not_finished(self):
        '''Change game result, game still in progress
        shortcut_name = 'Match en cours'
        '''
        if 0 <= self.index < len(self.data):
            game = self.data[self.index]
            game.not_finished()
            game.save()
            self.page.update()
