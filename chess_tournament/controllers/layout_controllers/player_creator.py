import inspect

from rich.layout import Layout
from rich.align import Align
from rich.console import RenderGroup
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.models.mymodels import Player
from .plugins import EditablePlugin, SelectablePlugin, CreatorPlugin


class PlayerCreatorLayoutController(CreatorPlugin, LayoutController):
    def __init__(self, *args, **kwargs):
    # name = models.FieldString()
    # firstname = models.FieldString()
    # birth = models.FieldDate()
    # # should create and use an option field
    # # sexe =  ...
    # # I should create and use a positive integer field
    # tournaments = models.Many2Many('Tournament', related_name='players')

    # rank = models.FieldInteger()
        name_fields = {
            'Nom': 'name',
            'Prénom': 'firstname',
            'Date de naissance': 'birth',
            'Rang': 'rank',
        }
        fields = {
            'Nom': '',
            'Prénom': '',
            'Date de naissance': '',
            'Rang': '',
        }
        super().__init__(
            model=Player,
            fields=fields,
            name_fields=name_fields,
            model_name='tournois',
            *args,
            **kwargs,
        )

    def after_creation(self, object_created: Player):
        self.popup_message = f'Le joueur "{object_created.name}" a bien été ajouté.'
