from datetime import date
# from .models.test import Player, Ref, Element
from .models.mymodels import Player, Tournament, GameType
# from chess_tournament.controllers import MainController


def run():
    p1 = Player(
        name='Bacrot',
        firstname='Étienne',
        birth=date(1983, 1, 22),
        rank=2678,
    )
    Tournament(
        name='World cup',
        place='Sochi, Russia',
        description=(
            'The Chess World Cup 2021 is a 206-player single-elimination '
            'chess tournament that is taking place in Sochi, Russia'
        ),
        players=[p1],
        nb_rounds=4,
        game_type=GameType(duration=10),
    )
    return
    # p1 = Player(rank=1, name='Plop')
    # p2 = Player(rank=2, name='Test')
    # e1 = Element()
    # Ref(e=e1, p=p1)
    return
    players = Player.all()
    print('\n\n Well Done !!')
    print(players)
    print(players[0].ref)
    # controller = MainController()
    # controller.loop()
