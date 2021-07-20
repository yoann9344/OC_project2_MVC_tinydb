from chess_tournament import models


class Player(models.Model):
    rank = models.FieldInteger(is_nullable=True)

    def increase_rank(self):
        self.rank += 1


class Ref(models.Model):
    e = models.ForeignKey('Element', related_name='ref')
    p = models.ForeignKey('Player', related_name='ref')


class Element(models.Model):
    pass
