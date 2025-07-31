import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class DB:
    """
    Represents a simple key-value database.

    Attributes:
      path (Optional[Path]): The path to the database file.
      db (dict): The database dictionary.
      rollback_key (Optional[str]): The key to rollback in case of an error.
    """
    path: Optional[Path] = None
    db: dict = field(default_factory=dict)
    rollback_key: Optional[str] = None

    def __post_init__(self):
        """
        Initializes the DB object by creating the database file if it doesn't exist and loading the data from the file.
        """
        if not self.path:
            return None
        self.path = Path(self.path)
        if not self.path.exists():
            self._create_db()
        if not self.db:
            self._load()

    def __iter__(self):
        """
        Initializes the iterator for the DB object.
        """
        self.current_index = 0
        self.keys = list(self.db.keys())
        return self

    def __next__(self):
        """
        Retrieves the next key in the database.
        """
        if self.current_index < len(self.keys):
            key = self.keys[self.current_index]
            self.current_index += 1
            return key
        raise StopIteration

    def _create_db(self):
        """
        Creates a new database file and dumps the current database dictionary into it.
        """
        with open(self.path, "w") as f:
            json.dump(self.db, f)

    def _load(self):
        """
        Loads the data from the database file into the database dictionary and migrates the data to a new hierarchical structure.
        """
        if not self.path:
            return None
        with open(self.path) as f:
            db = json.load(f)
            self.db = db
        # Migrate old flat structure to new hierarchical structure
        self._migrate_to_hierarchical()

    def _migrate_to_hierarchical(self):
        """Migrate old flat structure (provider::item) to hierarchical structure."""
        keys_to_migrate = []
        for key in list(self.db.keys()):
            if "::" in key and not isinstance(self.db[key], dict):
                keys_to_migrate.append(key)
        
        for key in keys_to_migrate:
            provider, item = key.split("::", 1)
            value = self.db.pop(key)  # Remove old flat key
            if provider not in self.db:
                self.db[provider] = {}
            self.db[provider][item] = value
        
        # Save the migrated structure if any changes were made
        if keys_to_migrate:
            self._save()

    def _save(self):
        """
        Saves the current database dictionary into the database file and handles exceptions by rolling back changes if necessary.
        """
        if not self.path:
            return None
        try:
            with open(self.path, "w") as f:
                json.dump(self.db, f, indent=6)
        except Exception as e:
            if self.rollback_key:
                print(f"Error saving database: {e}. Rolling back key '{self.rollback_key}'.")
                del self.db[self.rollback_key]
                self._save()
            raise e
            

    def transaction(func):
        """
        Decorator function for transaction management. Loads data before executing the function, saves data after execution, and returns the result.
        """
        def wrapper(self, *args, **kwargs):
            """
        Wrapper function for transaction management. Loads data before executing the function, saves data after execution, and returns the result.
        """
            self._load()
            res = func(self, *args, **kwargs)
            self._save()
            return res
        return wrapper

    @transaction
    def get(self, key):
        """
        Retrieves the value associated with the given key from the database, supporting both hierarchical and flat key formats.
        """
        if "::" in key:
            # New hierarchical key format: "provider::item" -> ["provider"]["item"]
            provider, item = key.split("::", 1)
            return self.db.get(provider, {}).get(item)
        else:
            # Support legacy flat keys for backward compatibility
            return self.db.get(key)

    @transaction
    def put(self, key, data):
        """
        Inserts or updates the value associated with the given key in the database, supporting both hierarchical and flat key formats. Handles rollback in case of an error.
        """
        self.rollback_key = key
        if "::" in key:
            # New hierarchical key format: "provider::item" -> ["provider"]["item"]
            provider, item = key.split("::", 1)
            if provider not in self.db:
                self.db[provider] = {}
            self.db[provider][item] = data
        else:
            # Fallback to flat structure for any edge cases
            self.db[key] = data
