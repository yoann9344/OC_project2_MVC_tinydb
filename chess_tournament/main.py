# from .models.test import Player, Ref, Element
from chess_tournament.controllers import MainController


def run():
    # p1 = Player(rank=1)
    # p2 = Player(rank=2)
    # e1 = Element()
    # Ref(e=e1, p=p1)
    # return
    # players = Player.all()
    # print('\n\n Well Done !!')
    # print(players)
    # print(players[0].ref)
    controller = MainController()
    controller.loop()
