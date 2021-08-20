from datetime import date
# from .models.test import Player, Ref, Element
from .models.mymodels import Player, Tournament, Date, GameType
from chess_tournament.controllers import MainController


def run():
    if len(Tournament.all()) == 0:
        GameType(duration=2)
        blitz = GameType(duration=5)
        GameType(duration=10)
        first_august = Date()
        p1 = Player(
            name='Bacrot',
            firstname='Étienne',
            birth=date(1983, 1, 22),
            rank=2678,
        )
        world_cup = Tournament(
            name='World cup',
            place='Sochi, Russia',
            description=(
                'The Chess World Cup 2021 is a 206-player single-elimination '
                'chess tournament that is taking place in Sochi, Russia'
            ),
            nb_rounds=4,
            game_type=blitz,
        )
        perray = Tournament(
            name='Perray',
            place='St Piere du Perray',
            description='Local tournament',
            nb_rounds=4,
            game_type=blitz,
        )
        perray.dates.append(first_august)
        perray.save()
        world_cup.dates.append(first_august)
        world_cup.players.append(p1)
        world_cup.save()
        # d1 = Date(tournament=perray)
        # d2 = Date(
        #     date=date.fromisoformat('2021-07-27'),
        #     tournament=world_cup
        # )
        # d2.save()
    today = Date.get(Date.date == date.today())
    # today = Date.get(Date.date == '2021-08-02')
    print(today.tournaments)

    # else:
    #     t1 = Tournament.get(doc_id=1)
    #     p1 = Player.get(doc_id=1)
    # return

    # # p1 = Player(rank=1, name='Plop')
    # # p2 = Player(rank=2, name='Test')
    # # e1 = Element()
    # # Ref(e=e1, p=p1)
    # return
    # players = Player.all()
    # print('\n\n Well Done !!')
    # print(players)
    # print(players[0].ref)

    # from chess_tournament.models import ModelMeta
    # print(ModelMeta.models.get('datetournament', None))
    # t = Tournament.all()
    # print(t[0].dates)
    # print(t[0].dates[0].tournament)

    controller = MainController()
    controller.loop()
