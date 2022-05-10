import base64
import typing as t
import uuid
from functools import wraps

import pydantic
import pydantic.generics
from google.cloud import datastore
from google.cloud.datastore.key import Key
from ndbmodels.connection import get_client

Id = t.Union[str, int]
Parent = t.Union[None, "Model", Key]


def generate_id() -> str:
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("ascii")[:-2]


def _inject_db(func):
    @wraps(func)
    def _inner(*args, **kwargs):
        return func(*args, **kwargs, db=get_client())

    return _inner


@_inject_db
def gen_key(
    kind: t.Type["Model"], id: Id, parent: Parent = None, *, db: datastore.Client
) -> Key:
    if isinstance(parent, Model):
        parent = parent.key

    return db.key(kind.__name__, id, parent=parent)


class NotFound(Exception):
    pass


MODEL_REGISTRY = {}


S = t.TypeVar("S", bound="Query")
T = t.TypeVar("T", bound="Model")
TK = t.Type[T]

QueryFilter = t.Tuple[str, str, t.Any]


def _chain(func: t.Callable[..., datastore.Query]):
    @wraps(func)
    def _inner(self: S, *args, **kwargs) -> S:
        query = func(self, *args, **kwargs)
        return self.__class__(self._kind, query)
        pass

    return _inner


class Query(t.Generic[T]):
    _query: datastore.Query
    _kind: t.Type[T]

    def __init__(self, kind: t.Type[T], query: datastore.Query):
        self._kind = kind
        self._query = query

    @_chain
    def filter(self, attr, func, value):
        return self._query.add_filter(attr, func, value)

    @_inject_db
    def __iter__(self, *, db: datastore.Client) -> t.Iterator[T]:
        for row in self._query.fetch():
            yield self._kind._from_entity(row)


class Model(pydantic.BaseModel):

    _key: t.Optional[Key] = pydantic.PrivateAttr(None)
    _parent: t.Optional["Model"] = pydantic.PrivateAttr(None)

    NotFound: t.ClassVar[t.Type[NotFound]]

    def __init_subclass__(cls) -> None:
        MODEL_REGISTRY[cls.__name__] = cls
        not_found = type(f"{cls.__name__}NotFound", (NotFound,), {})
        cls.NotFound = not_found
        return super().__init_subclass__()

    def __init__(self, id: t.Optional[Id] = None, parent: Parent = None, **kwargs):
        super().__init__(**kwargs)
        id = id or generate_id()
        self._key = gen_key(self.__class__, id, parent=parent)

    @classmethod
    def create(cls, **kwargs) -> "Model":
        inst = cls(**kwargs)
        inst.save()
        return inst

    @classmethod
    @_inject_db
    def query(cls, *, db):
        query = db.query(kind=cls.__name__)
        return Query[cls](cls, query)

    @property
    def id(self):
        return self.key.name

    @property
    def key(self):
        return self._key

    @property
    def parent(self):
        if self.key.parent and self._parent is None:
            parent_key = self.key.parent
            klass = MODEL_REGISTRY[parent_key.kind]
            self._parent = klass.get(parent_key.name)
        return self._parent

    @_inject_db
    def save(self, *, db: datastore.Client):
        db.put(self._to_entity())

    @classmethod
    def _from_entity(cls, entity: datastore.Entity):
        key = entity.key
        return cls(id=key.name, parent=key.parent, **entity)

    def _to_entity(self) -> datastore.Entity:
        entity = datastore.Entity(self.key)
        entity.update(self.dict())
        return entity

    @classmethod
    @_inject_db
    def get(cls, id: Id, parent: Parent = None, *, db: datastore.Client) -> "Model":
        key = gen_key(cls, id, parent)
        entity = db.get(key)
        if entity is None:
            raise NotFound()

        return cls._from_entity(entity)


class Course(Model):
    name: str
