import sys
from abc import ABC, ABCMeta

from tinydb import TinyDB, Query
from tinydb.queries import QueryInstance

from chess_tournament.app import app
import chess_tournament.models.fields as chess_fields
# from chess_tournament.models import ForeignKey, One2Many
# from chess_tournament.models


class Field(ABC):
    _type = None  # must be set

    def __init__(self, null_value=None, is_nullable=False, default=None):
        self.null_value = null_value
        self.is_nullable = is_nullable
        self._default = default

    @property
    def default(self):
        if self._default == self.null_value and not self.is_nullable:
            raise ValueError(
                f'Field {self} is not nullable and has no default value')
        return self._default

    def validate(self, value):
        if (
            value == self.null_value or
            (isinstance(self.null_value, set) and value in self.null_value)
        ):
            if not self.is_nullable:
                raise ValueError(
                    f'{self.__class__.__name__} can not be null')
        elif not isinstance(value, self._type):
            raise TypeError(
                f'{self.__class__.__name__} must be instance of {self._type} '
                f'not type {value}'
            )

    def serialize(self, value):
        return value


class ModelMeta(ABCMeta):
    models = {}

    def __new__(cls, name, bases, attrs):
        model_type = name.lower()
        model_class = super().__new__(cls, name, bases, attrs)
        model_class._fields = {}
        model_class._instances = {}
        model_class._table = model_class._db.table(model_type)
        if model_type in cls.models:
            raise ValueError(f'Model "{model_type}" is not uniq')
        else:
            cls.models[model_type] = model_class
            model_class._type = model_type

        for attr_name, field in model_class.__dict__.items():
            if isinstance(field, Field):
                model_class._fields[attr_name] = field

        app.register_model(model_type)
        return model_class

    def __call__(cls, *args, **kwargs):
        doc_id = kwargs.get('id', None)
        instance = cls._instances.get(doc_id, None)
        if instance is not None:
            return instance
        obj = super(Model, cls).__new__(cls)
        if doc_id is None:
            doc_id = obj._table.insert({})
        obj.id = doc_id
        cls._instances.update({doc_id: obj})
        obj.__init__(*args, **kwargs)
        return obj

    def __getattribute__(self, name: str):
        if name in super().__getattribute__('_fields'):
            return Query()[name]
        return super().__getattribute__(name)


class Model(metaclass=ModelMeta):
    _type = None
    _fields = {}
    _instances = {}
    _db = TinyDB('db.json')

    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            if name in kwargs:
                value = kwargs.pop(name)
                if self.init_O2M(name, value):
                    pass
                else:
                    if hasattr(field, 'deserialize'):
                        value = field.deserialize(value, name, self)
                    setattr(self, name, value)
            else:
                setattr(self, name, field.default)
        for name, value in kwargs.items():
            self.init_O2M(name, value)

        if kwargs.get('save', True):
            self.save()

    def init_O2M(self, name, value):
        if isinstance(value, dict) and '_table' in value:
            model: Model = ModelMeta.models.get(value['_table'], None)
            if model is not None:
                self._fields.update({
                    value['_table']: chess_fields.One2Many(model)
                })
                ids = value['_list']
                instances = [model.get(doc_id=doc_id) for doc_id in ids]
                setattr(self, name, instances)
                return True
            else:
                raise ValueError(
                    f"O2M : Model does not exist ({value['_table']}) "
                    'A migration might not been made !'
                )
        return False

    def save(self):
        if self.id is None:
            self.id = self._table.insert(self.serialize())
        else:
            self._table.update(self.serialize(), doc_ids=[self.id])

    def serialize(self):
        serialized = {}
        for name, value in self.__dict__.items():
            if name in self._fields:
                value = self.check_field_type(name, value)
                serialized[name] = self._fields[name].serialize(value)
        return serialized

    def __setattr__(self, name, value):
        if name in self._fields:
            value = self.check_field_type(name, value)
        super().__setattr__(name, value)

    def create_related_relationship(self, field, doc_id):
        related_obj: Model = field._type.get(doc_id=doc_id)
        if field.related_name:
            relations = getattr(related_obj, field.related_name, [])
            if not any(obj.id == self.id for obj in relations):
                relations.append(self)
                related_obj._fields.update(
                    {field.related_name: chess_fields.One2Many(self.__class__)}
                    # {field.related_name: One2Many(self.__class__)}
                )
                setattr(related_obj, field.related_name, relations)
                related_obj.save()
        return related_obj

    def check_field_type(self, name, value):
        field = self._fields[name]
        # if isinstance(field, ForeignKey):
        if isinstance(field, chess_fields.ForeignKey):
            if isinstance(value, int):
                value = self.create_related_relationship(field, value)
            elif isinstance(value, field._type):
                self.create_related_relationship(field, value.id)
            field.validate(value)
        else:
            field.validate(value)
        return value

    @classmethod
    def all(cls):
        return list(map(
            lambda obj: cls(**obj, id=obj.doc_id),
            cls._table.all()
        ))

    @classmethod
    def get(cls, query_instance: QueryInstance = None, doc_id: int = None):
        if doc_id is None and query_instance is None:
            raise TypeError(
                'get() missing 1 required argument: '
                "'query_instance' or 'doc_id'"
            )
        elif doc_id is not None:
            return cls(**cls._table.get(doc_id=doc_id), id=doc_id)
        objects = cls._table.search(query_instance)
        nb_obj = len(objects)
        if nb_obj > 1:
            raise ValueError('Multiple objects found')
        elif nb_obj == 0:
            return None
        else:
            instance = cls(**objects[0], id=objects[0].doc_id)
            return instance

    @classmethod
    def filter(
        cls,
        query_instance: QueryInstance = None,
        doc_ids: list[int] = []
    ):
        if not doc_ids and query_instance is None:
            raise TypeError(
                'get() missing 1 required argument: '
                "'query_instance' or 'doc_ids'"
            )
        elif doc_ids:
            return [cls.get(doc_id=doc_id) for doc_id in doc_ids]
        objects = cls._table.search(query_instance)
        return list(map(
            lambda obj: cls(**obj, id=obj.doc_id),
            objects
        ))

    def delete(self):
        id_ = self.id
        self._table.remove(doc_ids=[id_])
        self.__class__._instances.pop(id_)
