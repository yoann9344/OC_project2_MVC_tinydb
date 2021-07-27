import datetime

from chess_tournament import models


class Tournament(models.Model):
    name = models.FieldString()
    place = models.FieldString()
    nb_rounds = models.FieldInteger(default=4)
    game_type = models.FieldInteger()
    players = models.Many2Many('Player', related_name='tournaments')
    dates = models.Many2One('DateTournament', related_name='tournament')
    description = models.FieldString(is_nullable=True)

    def increase_rank(self):
        self.rank += 1

    def __str__(self):
        return self.name


class DateTournament(models.Model):
    date = models.FieldDate(default=datetime.date.today())
    tournament = models.ForeignKey(Tournament, related_name='dates')

    def __str__(self):
        return self.date.isoformat()


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='rounds')


class GameType(models.Model):
    duration = models.FieldInteger()

    def __str__(self):
        if self.duration <= 2:
            return 'Bullet'
        elif self.duration < 10:
            return 'Blitz'
        elif self.duration <= 60:
            return 'Rapid'
        else:
            return 'Standard'
