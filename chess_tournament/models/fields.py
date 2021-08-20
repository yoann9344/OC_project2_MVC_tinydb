import datetime
from functools import partial

from chess_tournament.app import app
from chess_tournament.models.model import ModelMeta, Model, Field, RelationalList


class RelationalField(Field):
    # WIP delete relationnal obj, required related name ?
    # def __init__(self, model: str or Model, related_name=None, *args, **kwargs):
    def __init__(self, model: str or Model, *args, related_name: str, **kwargs):
        self.related_name = related_name
        if isinstance(model, str):
            def get_model_from_string(model_name, field):
                field._type = ModelMeta.models[model_name.lower()]
            app.lazy_model_operation(
                partial(get_model_from_string, model, self),
                model
            )
        elif issubclass(model, Model):
            self._type = model
        else:
            raise TypeError('Relational Model is neither a str or a Model')
        super().__init__(*args, **kwargs)


class ForeignKey(RelationalField):
    _type = Model

    def serialize(self, value):
        return value.id


class Many2One(RelationalField):
    _type = Model

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, default=[], *args, **kwargs)

    def serialize(self, value):
        serialized = {
            '_table': self._type.__name__.lower(),
            '_list': list(map(lambda o: o.id, value))
        }
        if any(id_ is None for id_ in serialized['_list']):
            raise ValueError(f'id must integer {value}')
        return serialized

    def validate(self, value, attr, model):
        if (
            not isinstance(value, RelationalList)
            or not all(isinstance(obj, self._type) for obj in value)
        ):
            raise TypeError(
                f'{model.__class__.__name__}.{attr} must be type of '
                f'List[{self._type}] not {type(value)} : {value}'
            )


class Many2Many(Many2One):
    pass


class FieldInteger(Field):
    _type = int


class FieldFloating(Field):
    _type = float


class FieldString(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(null_value={None, ''}, *args, **kwargs)
    _type = str


class FieldDate(Field):
    _type = datetime.date

    def serialize(self, value: datetime.date or str or int):
        if isinstance(value, datetime.date):
            return value.isoformat()
        elif isinstance(value, str):
            # will raise an error if wrong format
            datetime.date.fromisoformat(value)
            return value
        elif isinstance(value, int):
            # will raise an error if wrong format
            d = datetime.date.fromtimestamp(value)
            return d.isoformat()

    def deserialize(self, value, name, model):
        if isinstance(value, datetime.date):
            return value
        elif isinstance(value, str):
            return datetime.date.fromisoformat(value)
        elif isinstance(value, int):
            return datetime.date.fromtimestamp(value)
        raise ValueError(
            f'Enable to deserialize field {name} from {model.__name__} :'
            f'value\'s type not handled : {value}'
        )
