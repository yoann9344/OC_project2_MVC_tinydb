import collections
import types
from abc import ABC, ABCMeta

from tinydb import TinyDB, Query
from tinydb.queries import QueryInstance

from chess_tournament.app import app
import chess_tournament.models.fields as chess_fields
# from chess_tournament.models import ForeignKey, Many2One
# from chess_tournament.models


class ObjectDoesNotExist(BaseException):
    pass


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

    def validate(self, value, attr, model):
        if (
            value == self.null_value or
            (isinstance(self.null_value, set) and value in self.null_value)
        ):
            if not self.is_nullable:
                raise ValueError(
                    f'{model.__class__.__name__}.{attr} can not be null')
        elif not isinstance(value, self._type):
            raise TypeError(
                f'{model.__class__.__name__}.{attr} must be instance of '
                f'{self._type} not type {value}'
            )

    def convert(self, value, attr, model):
        try:
            self.validate(value, attr, model)
        except TypeError:
            try:
                return self._type(value)
            except Exception:
                raise ValueError(
                    'Can not convert "{repr(value)}" to {self._type}')
        return value

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


class RelationalList(collections.UserList):
    def __init__(self, *args, model_obj, attr_name, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_obj = model_obj
        self.attr_name = attr_name

    def check(self):
        self.model_obj.check_field_type(self.attr_name, self)

    def append(self, *args, **kwargs):
        super().append(*args, **kwargs)
        self.check()

    def extend(self, *args, **kwargs):
        super().extend(*args, **kwargs)
        self.check()

    # WIP delete
    def pop(self, index, *args, **kwargs):
        # self.model_obj.delete(index)
        super().pop(index, *args, **kwargs)
        self.check()

    # WIP search
    # def index(self, *args, **kwargs):


class Model(metaclass=ModelMeta):
    _type = None
    _fields = {}
    _instances = {}
    _db = TinyDB('db.json')

    def __init__(self, **kwargs):
        # use list 'cause _fields can change at runtime
        for name, field in list(self._fields.items()):
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
        # for name, value in kwargs.items():
        #     self.init_O2M(name, value)

        if kwargs.get('save', True):
            self.save()

    def init_O2M(self, name, value):
        if isinstance(value, dict) and '_table' in value:
            model: Model = ModelMeta.models.get(value['_table'], None)
            if model is not None:
                field = self._fields[name]
                # related_name = None
                # for k, f in model._fields.items():
                #     if f._type == self.__class__:
                #         related_name = k
                #         break
                self._fields.update({
                   name: field.__class__(
                       model,
                       related_name=field.related_name,
                   )
                })
                ids = value['_list']
                self.__setattr__(name, RelationalList(
                    model_obj=self,
                    attr_name=name,
                ))
                instances = [model.get(doc_id=doc_id) for doc_id in ids]
                getattr(self, name).extend(instances)
                # instances_linked = RelationalList(
                #     instances,
                # )
                # setattr(self, name, instances_linked)
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

    def create_related_relationship(self, field, doc_id, name):
        related_obj: Model = field._type.get(doc_id=doc_id)
        related_name = field.related_name
        relation_type = field.__class__
        if relation_type == chess_fields.ForeignKey:
            relation_type = chess_fields.Many2One
        if related_name:
            must_be_saved = False
            relations = getattr(related_obj, related_name, [])
            if not isinstance(relations, RelationalList):
                if isinstance(relations, Field):
                    relations = []
                relations = RelationalList(
                    relations,
                    model_obj=related_obj,
                    attr_name=related_name,
                )
                must_be_saved = True
            if not any(obj.id == self.id for obj in relations):
                relations.append(self)
                related_obj._fields.update(
                    {
                        field.related_name: relation_type(
                            self.__class__,
                            related_name=name,
                        )
                    }
                )
                setattr(related_obj, field.related_name, relations)
                must_be_saved = True
            if must_be_saved:
                related_obj.save()
        return related_obj

    def check_field_type(self, name, value):
        # WIP key error if O2M not set, take care of related_name
        field = self._fields[name]
        # if isinstance(field, ForeignKey):
        if isinstance(field, chess_fields.ForeignKey):
            if isinstance(value, int):
                value = self.create_related_relationship(field, value, name)
            elif isinstance(value, field._type):
                self.create_related_relationship(field, value.id, name)
            field.validate(value, name, self)
        elif isinstance(field, chess_fields.Many2Many):
            for index, item in enumerate(value):
                if isinstance(item, int):
                    value[index] = self.create_related_relationship(
                        field, item, name
                    )
                elif isinstance(item, field._type):
                    self.create_related_relationship(field, item.id, name)
            if not isinstance(value, RelationalList):
                value = RelationalList(
                    value,
                    model_obj=self,
                    attr_name=name,
                )
            field.validate(value, name, self)
        elif isinstance(field, chess_fields.Many2One):
            for index, item in enumerate(value):
                if isinstance(item, int):
                    related_obj: Model = field._type.get(doc_id=item)
                    related_name = field.related_name
                    val = getattr(related_obj, related_name, None)
                    if val is None:
                        setattr(related_obj, related_name, self)
                    else:
                        # WIP error or unlink current foreign obj
                        pass
                elif isinstance(item, field._type):
                    related_name = field.related_name
                    val = getattr(item, related_name, None)
                    if val is None:
                        setattr(related_obj, related_name, self)
                    else:
                        # WIP error or unlink current foreign obj
                        pass
            if not isinstance(value, RelationalList):
                value = RelationalList(
                    value,
                    model_obj=self,
                    attr_name=name,
                )
            field.validate(value, name, self)
        else:
            field.validate(value, name, self)
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
            row = cls._table.get(doc_id=doc_id)
            if row is None:
                raise ObjectDoesNotExist(
                    f'{cls.__name__} with id={doc_id} does not exist.'
                )
            return cls(**row, id=doc_id)
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
        # WIP delete relations
        for name, field in self._fields.items():
            if isinstance(field, chess_fields.RelationalField):
                related_obj = getattr(self, name, None)
                if isinstance(related_obj, int):
                    related_obj = field._type(doc_id=related_obj)
                elif isinstance(related_obj, chess_fields.RelationalField):
                    continue
                elif related_obj is None:
                    continue
                related_name = field.related_name
                obj_has_many = isinstance(
                    field,
                    (chess_fields.ForeignKey, chess_fields.Many2Many)
                )
                for obj in list(related_obj):
                    if obj_has_many:
                        obj_references = getattr(obj, related_name, None)
                        if obj_references is not None:
                            nb_obj = len(obj_references)
                            for i, ref in enumerate(reversed(obj_references)):
                                if ref.id == self.id:
                                    obj_references.pop(nb_obj - i - 1)
                            obj.save()
                    else:
                        if isinstance(obj, chess_fields.RelationalField):
                            continue
                        setattr(obj, related_name, None)
                        obj.save()
        self._table.remove(doc_ids=[id_])
        self.__class__._instances.pop(id_)

    def __repr__(self):
        if isinstance(self.__str__, types.MethodWrapperType):
            return super().__repr__()
        else:
            return f'<{self.__class__.__name__} {str(self)}>'
