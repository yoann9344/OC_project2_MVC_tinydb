from chess_tournament import models


class Player(models.Model):
    name = models.FieldString()
    firstname = models.FieldString()
    birth = models.FieldDate()
    # should create and use an option field
    # sexe =  ...
    # I should create and use a positive integer field
    rank = models.FieldInteger()
