import pytest
from glasscandle.db import DB
from pathlib import Path


@pytest.fixture
def db_file(tmp_path):
    db_path = tmp_path / "test_db.json"
    return str(db_path)


def test_create_db(db_file):
    db = DB(path=db_file)
    assert db.path == Path(db_file)
    assert db.data == {}
    assert db.rollback_key is None


def test_load_existing_db(db_file):
    db = DB(path=db_file)
    db.data = {"provider": {"item": "value"}}
    db._save()
    loaded_db = DB(path=db_file)
    assert loaded_db.data == {"provider": {"item": "value"}}


def test_get_existing_key():
    db = DB()
    db.data = {"provider": {"item": "value"}}
    assert db.get("provider::item") == "value"


def test_get_non_existing_key():
    db = DB()
    db.data = {"provider": {"item": "value"}}
    assert db.get("provider::non_existing") is None


def test_get_legacy_key():
    db = DB()
    db.data = {"legacy_key": "value"}
    assert db.get("legacy_key") == "value"


def test_put_hierarchical_key():
    db = DB()
    db.put("provider::item", "value")
    assert db.data == {"provider": {"item": "value"}}


def test_put_legacy_key():
    db = DB()
    db.put("legacy_key", "value")
    assert db.data == {"legacy_key": "value"}


def test_put_existing_hierarchical_key():
    db = DB()
    db.data = {"provider": {"item": "old_value"}}
    db.put("provider::item", "new_value")
    assert db.data == {"provider": {"item": "new_value"}}


def test_put_existing_legacy_key():
    db = DB()
    db.data = {"legacy_key": "old_value"}
    db.put("legacy_key", "new_value")
    assert db.data == {"legacy_key": "new_value"}


def test_put_rollback_on_error(tmp_path, mocker):
    # Create a DB with a temp file path
    db_file = tmp_path / "test.json"
    db = DB(db_file)
    db.data = {"provider": {"item": "value"}}
    
    # Mock the _save method to raise an exception
    mock_save = mocker.patch.object(db, '_save')
    mock_save.side_effect = OSError("Simulated file write error")
    
    with pytest.raises(OSError):
        db.put("provider::item", "new_value")


def test_migrate_to_hierarchical():
    db = DB()
    db.data = {"provider::item": "value"}
    db._migrate_to_hierarchical()
    assert db.data == {"provider": {"item": "value"}}


def test_migrate_to_hierarchical_no_migration_needed():
    db = DB()
    db.data = {"provider": {"item": "value"}}
    db._migrate_to_hierarchical()
    assert db.data == {"provider": {"item": "value"}}
