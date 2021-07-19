import datetime
from abc import ABC
from functools import partial

from ..app import app
from .model import ModelMeta, Model


class Field(ABC):
    _type = None  # must be set

    def __init__(self, null_values={None}, is_nullable=False, default=None):
        self.null_values = null_values
        self.is_nullable = is_nullable
        self._default = default

    @property
    def default(self):
        if self._default in self.null_values and not self.is_nullable:
            raise ValueError(
                f'Field {self} is not nullable and has no default value')
        return self._default

    def validate(self, value):
        if value in self.null_values:
            if not self.is_nullable:
                raise ValueError(
                    f'{self.__class__.__name__} can not be null')
        if not isinstance(value, self._type):
            raise TypeError(
                f'{self.__class__.__name__} must be instance of {self._type} '
                f'not type {value}'
            )

    def serialize(self, value):
        return value


class RelationalField(Field):
    def __init__(self, model: str or Model, *args, **kwargs):
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

    def __init__(self, model, related_name: str = None, *args, **kwargs):
        self.related_name = related_name
        super().__init__(model, *args, **kwargs)


class One2Many(RelationalField):
    _type = Model

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)

    def serialize(self, value):
        serialized = {
            '_table': self._type.__name__.lower(),
            '_list': list(map(lambda o: o.id, value))
        }
        if any(id_ is None for id_ in serialized['_list']):
            raise ValueError(f'id must integer {value}')
        return serialized

    def validate(self, value):
        if (
            not isinstance(value, list)
            or not all(isinstance(obj, self._type) for obj in value)
        ):
            raise TypeError(
                f'{self.__class__.__name__} must be type of List[{self._type}]'
                f' not {value}'
            )


class Many2Many(One2Many):
    pass


class FieldInteger(Field):
    _type = int


class FieldFloating(Field):
    _type = float


class FieldString(Field):
    _type = str


class FieldDate(Field):
    _type = datetime.date
