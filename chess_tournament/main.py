from models.test import Player, Ref, Element


def run():
    p1 = Player(rank=1)
    p2 = Player(rank=2)
    e1 = Element()
    Ref(e=e1, p=p1)
