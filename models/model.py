from abc import ABCMeta, ABC
import datetime

from tinydb import TinyDB, Query
from tinydb.queries import QueryInstance


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


class FieldInteger(Field):
    _type = int


class FieldFloating(Field):
    _type = float


class FieldString(Field):
    _type = str


class FieldDate(Field):
    _type = datetime.date


class ModelMeta(ABCMeta):
    models = set()

    def __new__(cls, name, bases, attrs):
        model_class = super().__new__(cls, name, bases, attrs)
        model_class._fields = {}
        model_type = name.lower()
        if model_type in cls.models:
            raise ValueError(f'Model "{model_type}" is not uniq')
        else:
            cls.models.add(model_type)
            model_class._type = model_type

        for attr_name, field in model_class.__dict__.items():
            if isinstance(field, Field):
                model_class._fields[attr_name] = field

        return model_class

    def __getattribute__(self, name: str):
        if name in super().__getattribute__('_fields'):
            return Query()[name]
        return super().__getattribute__(name)


class Model(metaclass=ModelMeta):
    _fields = {}
    _db = TinyDB('db.json')

    def __init__(self, **kwargs):
        self.id = None
        for name, field in self._fields.items():
            print(name)
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                setattr(self, name, field.default)
        if kwargs.get('save', True):
            self.save()

    def save(self):
        print('save')
        if self.id is None:
            print(f'is None {self.id=}')
            self.id = self._db.insert(self.serialize())
        else:
            print(f'{self.id=}')
            self._db.update(self.serialize(), doc_ids=[self.id])

    def serialize(self):
        serialized = {'_type': self._type}
        for name, value in self.__dict__.items():
            if name in self._fields:
                self.check_field_type(name, value)
                if isinstance(value, Model):
                    serialized[name] = value.id
                else:
                    serialized[name] = value
        return serialized

    def __setattr__(self, name, value):
        if name in self._fields:
            self.check_field_type(name, value)
        super().__setattr__(name, value)

    # def __getattribute__(self, name):
    #     fields = super().__getattribute__('_fields')
    #     if name in fields:
    #         field = fields[name]
    #         if issubclass(field._type, Model):
    #             self.check_field_type(name, )
    #             setattr(
    #                 self,
    #                 name,
    #                 field._type(
    #                     **Model._db.get(doc_id=super().__getattribute__(name))
    #                 )
    #             )
    #     super().__getattribute__(name)

    def check_field_type(self, name, value):
        field = self._fields[name]
        if value in field.null_values:
            if not field.is_nullable:
                raise ValueError(
                    f'{self.__class__.__name__}.{name} can not be null')
        elif not isinstance(value, field._type):
            if issubclass(field._type, Model):
                if isinstance(value, int):
                    setattr(
                        self,
                        name,
                        field._type(Model._db.get(doc_id=value))
                    )
                    return
            raise ValueError(
                f'{self.__class__.__name__}.{name} '
                f'must be type of {field._type}'
            )

    @classmethod
    def get(cls, query_instance: QueryInstance):
        objects = cls._search(query_instance)
        nb_obj = len(objects)
        if nb_obj > 1:
            raise ValueError('Multiple objects found')
        elif nb_obj == 0:
            return None
        else:
            instance = cls(**objects[0], save=False)
            return instance

    @classmethod
    def filter(cls, query_instance: QueryInstance):
        objects = cls._search(query_instance)
        return list(map(lambda obj: cls(**obj, save=False), objects))

    @classmethod
    def _search(cls, query_instance: QueryInstance):
        print('Query', query_instance)
        q = query_instance & (Query()._type == cls._type)
        print('Query with type', q)
        serialized = cls._db.search(q)
        print(f'q : {serialized=}')
        return serialized


class ForeignKey(Field):
    _type = Model

    def __init__(self, model, *args, **kwargs):
        self._type = model
        super().__init__(*args, **kwargs)


class Player(Model):
    rank = FieldInteger(is_nullable=True)

    def increase_rank(self):
        self.rank += 1


class Ratatouille(Model):
    pass


class Tomatoes(Model):
    ratatouille = ForeignKey(Ratatouille)

print(Player._fields)
print(Ratatouille._fields)
print(Tomatoes._fields)


r = Ratatouille()
t1 = Tomatoes(ratatouille=r)
t2 = Tomatoes(ratatouille=r)
print(t1.serialize())
# # p = Player()
# # p.rank = 12
# # p.save()
# # p11: Player = Model._db.search(Player.rank == 11)
# p11: list[Player] = Player.filter(Player.rank < 12)
# # print(f'player query : {p11.serialize()}')
# print(f'player query : {p11}')
# p = Player()
# p.rank = 10
# p.save()
# p.increase_rank()
# p.save()
# p.rank = None
