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
    # game_type = models.FieldInteger()
    players = models.Many2Many('Player', related_name='tournaments')
    dates = models.Many2One('DateTournament', related_name='tournament')
    description = models.FieldString(is_nullable=True)
    rounds = models.Many2One('Round', related_name='tournament')

    def add_player(self, player: 'Player'):
        # does not add player if already in the tournament
        # neither if tournament has started (has rounds)
        if player not in self.players and not self.rounds:
            self.players.append(player)

    def __str__(self):
        return self.name


class DateTournament(models.Model):
    date = models.FieldDate(default=datetime.date.today())
    tournament = models.ForeignKey(Tournament, related_name='dates')

    def __str__(self):
        return self.date.isoformat()


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='rounds')
    players = models.Many2Many('Player', related_name='rounds')


class GameType(models.Model):
    duration = models.FieldInteger()
    tournaments = models.Many2One(Tournament, related_name='game_type')

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
