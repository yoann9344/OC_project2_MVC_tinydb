import collections
import datetime
from typing import TYPE_CHECKING

from chess_tournament import models

if TYPE_CHECKING:
    from . import Player


class Tournament(models.Model):
    name = models.FieldString()
    place = models.FieldString()
    nb_rounds = models.FieldInteger(default=4)
    game_type = models.ForeignKey('GameType', related_name='tournaments')
    players = models.Many2Many('Player', related_name='tournaments')
    dates = models.Many2Many('Date', related_name='tournaments')
    description = models.FieldString(is_nullable=True)
    rounds = models.Many2One('Round', related_name='tournament')

    def add_player(self, player: 'Player'):
        # does not add player if already in the tournament
        # neither if tournament has started (has rounds)
        if player not in self.players and not self.rounds:
            self.players.append(player)

    def get_current_round(self):
        try:
            return next(filter(lambda r: not r.is_finished(), self.rounds))
        except StopIteration:
            return None

    def __str__(self):
        return self.name


class Date(models.Model):
    date = models.FieldDate(default=datetime.date.today())
    tournaments = models.Many2Many(Tournament, related_name='dates')

    def __new__(cls, *args, date=datetime.date.today(), **kwargs):
        '''Do not duplicate the date if it already exist
        '''
        kwargs['date'] = date
        if kwargs.get('id', None) is not None:
            return super().__new__(cls, *args, **kwargs)
        try:
            return cls.get(cls.date == date)
        except models.ObjectDoesNotExist:
            return super().__new__(cls, *args, **kwargs)

    def __str__(self):
        return self.date.isoformat()


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='rounds')
    name = models.FieldString(default='Round')
    games = models.Many2One('Game', related_name='turn')

    def is_finished(self):
        if not self.games:
            return False
        else:
            return all(game.is_finished() for game in self.games)

    def get_players_score(self):
        players_points = collections.Counter()
        for game in self.games:
            players_points.update({
                game.white.id: game.white_points(),
                game.black.id: game.black_points(),
            })
        return players_points


class Game(models.Model):
    turn = models.ForeignKey('Round', related_name='games')
    white = models.ForeignKey('Player', related_name='games_with_white')
    black = models.ForeignKey('Player', related_name='games_with_black')
    result = models.FieldInteger(default=0)

    @property
    def score(self):
        try:
            white_points = self.white_points()
        except ValueError:
            return '0 - 0'
        if self.result == 0:
            return '0 - 0'
        elif white_points == 1:
            return '1 - 0'
        elif white_points == 0:
            return '0 - 1'
        else:
            return '\u00BD - \u00BD'

    def white_won(self):
        self.result = 1

    def black_won(self):
        self.result = 2

    def equality(self):
        self.result = 3

    def not_finished(self):
        self.result = 0

    def white_points(self):
        if self.result == 0:
            return 0
        elif self.result == 1:
            return 1
        elif self.result == 2:
            return 0
        elif self.result == 3:
            return 0.5
        else:
            raise ValueError(
                'The result must be between 0 and 3 (inclusiv), '
                "use Model's methods"
            )

    def black_points(self):
        if self.result == 0:
            return 0
        else:
            return 1 - self.white_points()

    def is_finished(self):
        return self.result != 0


class GameType(models.Model):
    duration = models.FieldInteger()
    tournaments = models.Many2One(Tournament, related_name='game_type')

    def __new__(cls, *args, duration, **kwargs):
        '''Do not duplicate the game type if it already exist
        '''
        kwargs['duration'] = duration
        if kwargs.get('id', None) is not None:
            return super().__new__(cls, *args, **kwargs)
        try:
            return cls.get(cls.duration == duration)
        except models.ObjectDoesNotExist:
            return super().__new__(cls, *args, **kwargs)

    def get_type_name(self):
        return str(self).lower()

    def __str__(self):
        if self.duration <= 2:
            return 'Bullet'
        elif self.duration < 10:
            return 'Blitz'
        elif self.duration <= 60:
            return 'Rapid'
        else:
            return 'Standard'
