import typing as t
from contextlib import contextmanager
from functools import wraps

from ndbmodels.connection import get_client

if t.TYPE_CHECKING:
    from ndbmodels.model import Model  # noqa: F401


@contextmanager
def transaction():
    client = get_client()
    with client.transaction():
        yield


def atomic(func):
    @wraps(func)
    def _inner(*args, **kwargs):
        with transaction():
            return func(*args, **kwargs)

    return _inner


Instances = t.TypeVar("Instances", bound=t.Iterable["Model"])


def save_multi(instances: Instances) -> Instances:
    client = get_client()
    client.put_multi([inst._to_entity() for inst in instances])
    return instances
