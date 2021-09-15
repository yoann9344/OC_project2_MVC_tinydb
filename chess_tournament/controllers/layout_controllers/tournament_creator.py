import inspect

from rich.layout import Layout
from rich.align import Align
from rich.console import RenderGroup
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from chess_tournament.controllers.layout_controller import LayoutController
from chess_tournament.models.mymodels import Tournament, GameType
from .plugins import EditablePlugin, SelectablePlugin, CreatorPlugin


class TournamentCreatorLayoutController(CreatorPlugin, LayoutController):
    def __init__(self, *args, **kwargs):
        name_fields = {
            'Nom': 'name',
            'Lieu': 'place',
            'Description': 'description',
            'Nombre de tours': 'nb_rounds',
            'Durée de la partie': 'game_type',
        }
        fields = {
            'Nom': '',
            'Lieu': '',
            'Description': '',
            'Nombre de tours': '',
            'Durée de la partie': '',
        }
        super().__init__(
            model=Tournament,
            fields=fields,
            name_fields=name_fields,
            model_name='tournois',
            *args,
            **kwargs,
        )

    def convert_field(self, name, value):
        if name == 'game_type':
            assert value != ''
            duration = int(value)
            value = GameType(duration=duration)
        else:
            value = Tournament._fields[name].convert(value, name, Tournament)
        return value

    def after_creation(self, object_created):
        from chess_tournament.controllers.pages import TournamentManagerPage
        self.page.loop.go_to(
            TournamentManagerPage(
                loop=self.page.loop,
                tournament=object_created,
            )
        )

    def validate_field_input(self, name, input_value):
        if name == 'game_type':
            assert input_value != ''
            int(input_value)
        else:
            Tournament._fields[name].convert(
                input_value, name, Tournament
            )

# class TournamentCreatorLayoutController(LayoutController, EditablePlugin, SelectablePlugin):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.data = None

#         self.shortcuts = {
#             'k': self.up,
#             'j': self.down,
#             'i': self.edit,
#             'g': self.create_tournament,
#         }
#         self.info_color = ''
#         self.multiple_selection_color = 'green'
#         self.double_selection_color = 'yellow'
#         self.single_selection_color = 'blue'
#         self.error = ''

#         self.explainations = inspect.cleandoc('''
#             ### Création d'un tournois
#             - Sélectionnez les champs à renseigner avec <k> et <j>
#             - Éditez le champs sélectionné avec <e>
#             - Validez la selection avec <tab> ou <entrée>
#             - Quand tous les champs sont remplis (vert ou jaune)
#             appuyez sur <g> pour créer le tournois.
#         ''')
#         # self.fields = [
#         #     Text.assemble('Nom : ', 'TRUC'),
#         #     Text.assemble('Descrption : ', ''),
#         #     Text.assemble('Nombre de tours : ', ''),
#         # ]
#         self.name_fields = {
#             'Nom': 'name',
#             'Lieu': 'place',
#             'Description': 'description',
#             'Nombre de tours': 'nb_rounds',
#             'Durée de la partie': 'game_type',
#         }
#         self.fields = {
#             'Nom': '',
#             'Lieu': '',
#             'Description': '',
#             'Nombre de tours': '',
#             'Durée de la partie': '',
#         }

#         self.init_fields()

#         # self.fields = {
#         #     ('Nom': 'PLOP'),
#         #     ('Description': ''),
#         #     ('Nombre de tours': ''),
#         # }
#         # self.selectables = [Text.assemble(k + ' : ', v) for k, v in self.fields.items()]
#         # self.groups = RenderGroup(
#         #     Markdown(self.explainations),
#         #     # *self.fields,
#         #     *self.selectables,
#         # )
#         # self.align = Align.center(
#         #     # Markdown(self.explainations),
#         #     self.groups,
#         #     vertical='middle'
#         # )
#         self.panel_view = Panel(
#             '',
#             style='',
#             title='',
#             border_style=self.border_style,
#         )
#         self.index = 0
#         self.page.update_by_controller(self)

#     def update(self, layout: Layout):
#         # self.align.renderable = Markdown(self.welcome_message)
#         # self.selectables = [Text.assemble(k + ' : ', v) for k, v in self.fields.items()]
#         self.selectables = []
#         for index, kv in enumerate(self.fields.items()):
#             k, v = kv
#             if index in self.multiple_selection:
#                 if self.index == index:
#                     style = self.double_selection_color
#                 else:
#                     style = self.multiple_selection_color
#             else:
#                 if self.index == index:
#                     style = self.single_selection_color
#                 else:
#                     style = None
#             self.selectables.append(Text.assemble(k + ' : ', v, style=style))
#         if 0 <= self.index < len(self.selectables) and self.info_color:
#             self.selectables[self.index].style = self.info_color

#         self.groups = RenderGroup(
#             Markdown(self.explainations),
#             *self.selectables,
#             self.error
#         )
#         self.align = Align.center(
#             # Markdown(self.explainations),
#             self.groups,
#             vertical='middle'
#         )
#         self.panel_view = Panel(
#             self.align,
#             style='',
#             title='',
#             border_style=self.border_style,
#         )
#         layout.update(self.panel_view)

#     def edit(self):
#         """Edit mode test.

#         shortcut_name = Éditer
#         """
#         if 0 <= self.index < len(self.selectables):
#             # self.activate_edition(callback=self.buffer, multiline=True)
#             self.activate_edition(callback=self.buffer, multiline=False)

#     def init_fields(self):
#         self.multiple_selection.clear()
#         for index, name in enumerate(self.fields):
#             field_name = self.name_fields[name]
#             field = Tournament._fields[field_name]
#             if field._default is not None:
#                 self.fields[name] = str(field._default)
#                 self.multiple_selection.add(index)
#             elif field.is_nullable:
#                 self.multiple_selection.add(index)
#             else:
#                 self.fields[name] = ''

#     def create_tournament(self):
#         """Create tournament and open TournamentManegerPage.

#         shortcut_name = Créer le tournois
#         """
#         params = {}
#         if len(self.multiple_selection) != len(self.fields):
#             self.error = 'Veuillez remplir les champs (ils doivent devenir verts)'
#             self.page.update_by_controller(self)
#             return
#         for name, value in self.fields.items():
#             attr = self.name_fields[name]
#             try:
#                 if attr == 'game_type':
#                     assert value != ''
#                     duration = int(value)
#                     value = GameType(duration=duration)
#                 else:
#                     value = Tournament._fields[attr].convert(value, attr, Tournament)
#             except Exception as error:
#                 self.error = 'Plop' + str(error)
#                 break
#             params[attr] = value
#         else:
#             tournament = Tournament(**params)
#             self.init_fields()
#             from chess_tournament.controllers.pages import TournamentManagerPage
#             self.page.loop.go_to(
#                 TournamentManagerPage(
#                     loop=self.page.loop,
#                     tournament=tournament,
#                 )
#             )
#         self.page.update_by_controller(self)

#     def validate_input(self, field_name, input_ended):
#         input_value = self.fields[field_name]
#         attr = self.name_fields[field_name]
#         try:
#             if attr == 'game_type':
#                 assert input_value != ''
#                 int(input_value)
#             else:
#                 Tournament._fields[attr].convert(
#                     input_value, attr, Tournament
#                 )
#             validated = True
#             self.info_color = 'underline green'
#         except Exception:
#             validated = False
#             self.error = ''
#             self.info_color = 'underline red'
#         if input_ended:
#             self.info_color = ''
#             next_index = self.index + 1
#             if not validated:
#                 self.fields[field_name] = ''
#                 if self.index in self.multiple_selection:
#                     self.multiple_selection.remove(self.index)
#             elif (
#                 next_index < len(self.selectables) and
#                 next_index not in self.multiple_selection
#             ):
#                 self.multiple_selection.add(self.index)
#                 # self.select()
#                 self.index += 1
#             else:
#                 # Handle !
#                 # self.select()
#                 self.multiple_selection.add(self.index)
#                 for i in range(len(self.selectables)):
#                     if i not in self.multiple_selection:
#                         self.index = i
#                         break
#                 else:
#                     self.allgreen = True

#     def buffer(self, buffer, last_entries, desactivated, cancelled):
#         if cancelled:
#             buffer = ''
#         field_name = list(self.fields.keys())[self.index]
#         self.fields[field_name] = buffer
#         self.validate_input(field_name, desactivated)
#         self.page.update_by_controller(self)
