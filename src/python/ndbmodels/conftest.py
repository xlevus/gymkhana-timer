import os
import uuid

import pytest
from ndbmodels import connection


@pytest.fixture
def db_namespace() -> str:
    return f"test-{uuid.uuid4()}"


@pytest.fixture(autouse=True)
def db(db_namespace):
    os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"

    yield connection.connect("testing", db_namespace)
