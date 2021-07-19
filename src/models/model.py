from abc import ABCMeta

from tinydb import TinyDB, Query
from tinydb.queries import QueryInstance

from ..app import app
from .fields import Field, ForeignKey, One2Many


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

    def __getattribute__(self, name: str):
        if name in super().__getattribute__('_fields'):
            return Query()[name]
        return super().__getattribute__(name)


class Model(metaclass=ModelMeta):
    _fields = {}
    _instances = {}
    _db = TinyDB('db.json')

    def __new__(cls, *args, **kwargs):
        instance = cls._instances.get(kwargs.get('id', None), None)
        if instance is not None:
            instance._instance_initialized = True
            return instance
        return super(Model, cls).__new__(cls)

    def __init__(self, **kwargs):
        if getattr(self, '_instance_initialized', False):
            return
        self.id = kwargs.get('id', None)
        if self.id is None:
            # pre-save column
            self.id = self._table.insert({})
        try:
            for name, field in self._fields.items():
                if name in kwargs:
                    setattr(self, name, kwargs.pop(name))
                else:
                    setattr(self, name, field.default)
            for name, value in kwargs.items():
                if isinstance(value, dict) and '_table' in value:
                    model: Model = ModelMeta.models.get(value['_table'], None)
                    if model is not None:
                        self._fields.update({value['_table']: model})
                        ids = value['_list']
                        instances = [model.get(doc_id=doc_id) for doc_id in ids]
                        setattr(self, name, instances)
        except Exception as error:
            if kwargs.get('id', None) is None:
                # delete pre-saved column
                self.delete()
            raise error

        if kwargs.get('save', True):
            self.save()
            self.__class__._instances.update({self.id: self})

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
                    {field.related_name: One2Many(self.__class__)}
                )
                setattr(related_obj, field.related_name, relations)
                related_obj.save()
        return related_obj

    def check_field_type(self, name, value):
        field = self._fields[name]
        if isinstance(field, ForeignKey):
            if isinstance(value, int):
                value = self.create_related_relationship(field, value)
            elif isinstance(value, field._type):
                self.create_related_relationship(field, value.id)
            field.validate(value)
        else:
            field.validate(value)
        return value

    @classmethod
    def get(cls, query_instance: QueryInstance = None, doc_id: int = None):
        if doc_id is None and query_instance is None:
            raise TypeError(
                'get() missing 1 required argument: '
                "'query_instance' or 'doc_id'"
            )
        elif doc_id is not None:
            return cls(**cls._table.get(doc_id=doc_id), id=doc_id, save=False)
        objects = cls._table.search(query_instance)
        nb_obj = len(objects)
        if nb_obj > 1:
            raise ValueError('Multiple objects found')
        elif nb_obj == 0:
            return None
        else:
            instance = cls(**objects[0], id=objects[0].doc_id, save=False)
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
            lambda obj: cls(**obj, id=obj.doc_id, save=False),
            objects
        ))

    def delete(self):
        self._table.remove(doc_ids=[self.id])


from .fields import FieldInteger
class Player(Model):
    rank = FieldInteger(is_nullable=True)
    # tournament = Many2Many(Tournaments)

    def increase_rank(self):
        self.rank += 1


class Ref(Model):
    e = ForeignKey('Element', related_name='ref')
    p = ForeignKey('Player', related_name='ref')


class Element(Model):
    pass


p1 = Player(rank=1)
p2 = Player(rank=2)
e1 = Element()
Ref(e=e1, p=p1)
