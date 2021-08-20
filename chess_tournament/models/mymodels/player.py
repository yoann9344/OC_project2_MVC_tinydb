from chess_tournament import models


class Player(models.Model):
    name = models.FieldString()
    firstname = models.FieldString()
    birth = models.FieldDate()
    # should create and use an option field
    # sexe =  ...
    # I should create and use a positive integer field
    tournaments = models.Many2Many('Tournament', related_name='players')
    rank = models.FieldInteger()
    games_with_white = models.Many2One('Game', related_name='white')
    games_with_black = models.Many2One('Game', related_name='black')

    def __str__(self):
        return self.name
