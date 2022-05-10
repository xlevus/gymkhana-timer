import pytest
from ndbmodels.model import Model, generate_id
from ndbmodels.transaction import atomic, save_multi


def test_generate_id():
    id = generate_id()
    assert isinstance(id, str)

    id2 = generate_id()
    assert id != id2


class AModel(Model):
    value: str


class TestModel:
    def test_save(self, db):
        instance = AModel(value="fred")
        instance.save()

        assert instance.id is not None

        key = instance.key
        assert key.kind == "AModel"

        (row,) = list(db.query(kind="AModel").fetch(10))
        assert row["value"] == "fred"
        assert set(row.keys()) == {"value"}

    def test_save_parent(self, db):
        parent = AModel(value="parent")
        child = AModel(value="child", parent=parent)
        parent.save()
        child.save()
        assert child.key.parent == parent.key

    def test_get(self, db):
        instance = AModel(value="fred")
        instance.save()

        instance2 = AModel.get(instance.id)
        assert isinstance(instance2, AModel)
        assert instance2.key == instance.key
        assert instance2.value == instance.value

    def test_parent(self, db):
        parent = AModel(value="parent")
        child = AModel(value="child", parent=parent)
        parent.save()
        child.save()

        parent2 = child.parent
        assert isinstance(parent2, AModel)
        assert parent2.id == parent.id
        assert parent2.value == parent.value


class TestQuery:
    @pytest.fixture
    @atomic
    def instances(self):
        return save_multi(
            [AModel(value=char) for char in ("a", "b", "c", "d", "e", "f", "g")]
        )

    def test_empty_query(self):
        assert list(AModel.query()) == []

    def test_query(self, instances):
        results = list(AModel.query())

        assert len(results) == len(instances)

    def test_filter(self, instances):
        results = list(AModel.query().filter("value", "=", "a"))
        assert len(results) == 1
