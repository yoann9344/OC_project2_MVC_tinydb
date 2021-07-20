import datetime

from chess_tournament import models


class Tournament(models.Model):
    name = models.FieldString()
    place = models.FieldString()
    nb_rounds = models.FieldInteger(default=4)
    game_type = models.ForeignKey('GameType')
    # dates = models.One2Many()
    description = models.FieldString(is_nullable=True)

    def increase_rank(self):
        self.rank += 1


class DateTournament(models.Model):
    date = models.FieldDate(default=datetime.date.today())
    tournament = models.ForeignKey(Tournament, related_name='dates')


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='rounds')


class GameType(models.Model):
    # should create and use option field
    duration = models.FieldInteger()
