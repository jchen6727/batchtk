import os, pandas, numpy, sqlite3, io, pickle
import numpy
from typing import Any
from batchtk.utils.misc import expand_path
from batchtk.utils.serializer import SQLiteTypeRule
from batchtk.utils.mixins import StateMixin

from collections import namedtuple


class Storage(object):
    def __init__(self):
        pass

    def insert(self, entry: dict):  # replace log with "insert" // see below
        pass

    def find(self, key, value):
        pass

    def close(self):
        pass


class SQLStorage(Storage):  # Use as TrialTable or Table object nomenclature to avoid confusion with logger
    def __init__(self):
        super().__init__()
        self.path = None

    def init_db(self):  # initializes the database
        pass

    def read_schema(self):  # get the schema of the storage
        pass

    def add_columns(self, schema: dict):  # add new columns to storage
        pass

    def insert(self, entry: dict):  # replace log with "insert" // see below
        pass

    def find(self, key, value):
        pass

    def close(self):
        pass


### handle the serialization of numpy objects with global adapter registration...

SQLiteTypeRuleResult = namedtuple('SQLiteTypeRuleResult', ['type', 'adapter'])


def _SQLiteINTEGERRule(val: Any) -> SQLiteTypeRuleResult | None:
    """return SQLiteTypeRuleResult("INTEGER", int) for all numpy integer types. else returns None, None"""
    return SQLiteTypeRuleResult("INTEGER", int) if isinstance(val, numpy.integer) else None


def _SQLiteREALRule(val: Any) -> SQLiteTypeRuleResult | None:
    """return SQLiteTypeRuleResult("REAL", float) for all numpy floating types. else returns None"""
    return SQLiteTypeRuleResult("REAL", float) if isinstance(val, numpy.floating) else None


def _SQLitePBLOBAdapter(val: Any) -> memoryview:
    """serialize any object to a pickled blob."""
    return sqlite3.Binary(pickle.dumps(val))


def _SQLitePBLOBConverter(blob: bytes) -> Any:
    """deserialize any object from a pickled blob."""
    return pickle.loads(blob)


def check_default(val: Any, default: Any):
    if val is None:
        return default
    return val


class SQLiteStorage(SQLStorage, StateMixin):  # SQLiteTable...

    # relevant for adding columns to schema
    # serves as the initial LUT for type inference
    # any key in _DEFAULT_TYPE_MAP is considered registered --- that is
    # an ADAPTER is registered for that type (and a CONVERTER if necessary)
    _DEFAULT_TYPE_MAP = {  # serves as the initial LUT for type inference
        numpy.int64: "INTEGER",
        numpy.float64: "REAL",
        bool: "INTEGER",
        int: "INTEGER",
        float: "REAL",
        str: "TEXT",
    }

    _DEFAULT_TYPE_RULES = [
        SQLiteTypeRule(function=_SQLiteINTEGERRule, priority=0),
        SQLiteTypeRule(function=_SQLiteREALRule, priority=1),
    ]

    _DEFAULT_ADAPTERS = [
        (numpy.int64, int),  # calls int on numpy.integer
        (numpy.float64, float),  # calls float on numpy.floating
    ]

    _DEFAULT_CONVERTERS = [
        ("PBLOB", _SQLitePBLOBConverter)
    ]

    # Updated transient attributes to include the caches
    _transient_attributes = ['_oe', '_connect', 'type_map', 'type_rules']

    def __init__(self,
                 label: str = 'trials',
                 directory: str = '.',
                 filename: str = None,
                 schema: dict = None,
                 default_type: str = 'PBLOB',
                 timeout: int = 30,
                 type_map: dict = None,
                 type_rules: list = None,
                 adapters: list = None,
                 converters: list = None,
                 ):
        ## handle the serialization of numpy objects
        super().__init__()
        directory = expand_path(directory)
        os.makedirs(directory, exist_ok=True)
        self.label = label
        self.schema = schema or dict()
        filename = filename or "{}.sqlite.db".format(label)
        self.path = "{}/{}".format(directory, filename)
        self.timeout = timeout

        # Store configs for restoration
        self.type_map_config = check_default(type_map, self._DEFAULT_TYPE_MAP)
        self.type_rules_config = check_default(type_rules, self._DEFAULT_TYPE_RULES)
        self.adapters_config = check_default(adapters, self._DEFAULT_ADAPTERS)
        self.converters_config = check_default(converters, self._DEFAULT_CONVERTERS)

        # Define the blueprint for state recreation
        self.state_config = {
            '_connect': sqlite3.connect,
            '_oe': sqlite3.OperationalError,
            'type_map': {
                '_constructor_': self.type_map_config.copy
            },
            'type_rules': {
                '_constructor_': self.type_rules_config.copy
            },
        }

        # Build the initial state (registers defaults and sets up caches)
        self._recreate_state_from_config()

        self.default_type = default_type
        self.init_db()

    def _wal_connect(self, timeout=None):
        timeout = timeout or self.timeout
        conn = self._connect(self.path, timeout=timeout, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _recreate_state_from_config(self):
        """
        Rebuilds transient state and restores the environment.
        Normalizes type_map to ensure high cohesion (always SQLiteTypeRuleResult).
        """
        # 1. Rebuild attributes via Mixin (including raw type_map from config)
        super()._create_state_from_config()

        # 2. Re-register DEFAULT environment adapters
        # We do this first to ensure a baseline of known adapters exists
        adapter_lookup = dict(self.adapters_config)
        for py_type, adapter in self.adapters_config:
            sqlite3.register_adapter(py_type, adapter)

        for py_type, converter in self.converters_config:
            sqlite3.register_converter(py_type, converter)

        # 3. Normalize type_map and Re-register adapters
        # We convert any legacy strings in type_map to SQLiteTypeRuleResult
        if hasattr(self, 'type_map'):
            for py_type, val in list(self.type_map.items()):
                # Normalization Step: String -> Result
                if isinstance(val, str):
                    # Look up the corresponding adapter, or None if native
                    adapter = adapter_lookup.get(py_type)
                    result_obj = SQLiteTypeRuleResult(val, adapter)
                    self.type_map[py_type] = result_obj
                else:
                    result_obj = val

                # Registration Step: Ensure the adapter is active in this process
                if result_obj.adapter and callable(result_obj.adapter):
                    sqlite3.register_adapter(py_type, result_obj.adapter)

    def read_schema(self):
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info({})".format(self.label))
            data = cursor.fetchall()
        schema = {column[1]: column[2] for column in data}
        return schema

    def _sync_schema(self):
        schema = self.read_schema()
        check_columns = self.schema.keys() & schema.keys()
        write_columns = {key: self.schema[key] for key in self.schema.keys() - schema.keys()}
        if not all(schema[key] == self.schema[key] for key in check_columns):
            raise ValueError(
                f"provided schema of SQLiteStorage conflicts datatypes with existing schema at path: {schema} != {self.schema}")
        if write_columns:
            self.add_columns(write_columns)
        self.schema.update(schema)

    def _create_db(self):
        if not self.schema:
            exec_str = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        else:
            exec_str = "id INTEGER PRIMARY KEY AUTOINCREMENT, {}".format(
                ','.join(["[{}] {}".format(k, v) for k, v in self.schema.items()]))
        exec_str = "CREATE TABLE IF NOT EXISTS {} ({})".format(self.label, exec_str)
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(exec_str)
            conn.commit()

    def init_db(self):
        if os.path.exists(self.path):
            self._sync_schema()
            return
        self._create_db()

    def insert(self, entry: dict, allow_schema_updates: bool = True):
        # --- STEP 1: JIT Registration ---
        # Always learn/check types first to ensure adapters are registered
        # This prevents the crash when using an explicit schema with unknown types
        for val in entry.values():
            self.infer_and_register_type(val)

        # --- STEP 2: Schema Evolution ---
        diff = entry.keys() - self.schema.keys()
        if allow_schema_updates:
            # We reuse the inference logic to get the SQL type strings
            diff = {key: self.infer_and_register_type(entry[key]) for key in diff}
            self.add_columns(diff)

        if diff and not allow_schema_updates:
            raise ValueError(f"entry keys {diff} do not exist in the db schema and allow_schema_updates set to False.")

        keys, vals = zip(*entry.items())
        exec_str = "INSERT INTO {} ([{}]) VALUES ({})".format(self.label, '],['.join(keys), ','.join(['?'] * len(vals)))
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(exec_str, vals)
            conn.commit()

    def infer_and_register_type(self, val: Any) -> str:
        val_type = type(val)

        # 1. Check Cache
        # Because of _recreate_state_from_config, we assume the cache is cohesive
        # and contains SQLiteTypeRuleResult objects.
        cached = self.type_map.get(val_type, None)
        if cached:
            return cached.type

        # 2. Run Rules
        for rule in self.type_rules:
            inferred = rule(val)
            if inferred:
                # Save the FULL result (Type + Adapter) to the map
                self.type_map[val_type] = inferred
                # Register the side effect
                sqlite3.register_adapter(val_type, inferred.adapter)
                return inferred.type

        # 3. Defaults
        if self.default_type == 'TEXT':
            result = SQLiteTypeRuleResult("TEXT", str)
            self.type_map[type(val)] = result
            sqlite3.register_adapter(type(val), str)
            return 'TEXT'

        if self.default_type == 'PBLOB':
            result = SQLiteTypeRuleResult("PBLOB", _SQLitePBLOBAdapter)
            self.type_map[type(val)] = result
            sqlite3.register_adapter(type(val), _SQLitePBLOBAdapter)
            return 'PBLOB'

        raise (
            RuntimeError("no type inference for {}, and default_type {} not recognized".format(val, self.default_type)))

    def add_columns(self, columns: list | tuple | dict) -> list[tuple[str, Exception]]:
        if isinstance(columns, (list, tuple)):
            new_columns = {column: self.default_type for column in columns if column not in self.schema.keys()}
        if isinstance(columns, dict):
            check_columns = self.schema.keys() & columns.keys()
            if not all(self.schema[key] == columns[key] for key in check_columns):
                raise ValueError(
                    f"columns dict provided {columns} conflicts with schema of SQLiteStorage: {self.schema} != {columns}")
            new_columns = {key: value for key, value in columns.items() if key not in self.schema.keys()}
        exec_strs = ["ALTER TABLE {} ADD COLUMN [{}] {}".format(self.label, new_column, new_value)
                     for new_column, new_value in new_columns.items()]
        oe = []
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            for new_column, exec_str in zip(new_columns.keys(), exec_strs):
                try:
                    cursor.execute(exec_str)
                    oe.append((new_column, None))
                except self._oe as e:
                    oe.append((new_column, e))
            conn.commit()
        self.schema = self.read_schema()
        return oe

    def to_df(self):
        exec_str = "SELECT * FROM {}".format(self.label)
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(exec_str)
            rows = cursor.fetchall()
            description = cursor.description
        columns = [column[0] for column in description]
        df = pandas.DataFrame(rows, columns=columns)
        return df

    def find(self, key: str, value: Any):
        if key not in self.schema:
            raise ValueError(f"column {key} does not exist in the db schema: {self.schema}")
        exec_str = "SELECT * FROM {} WHERE {} = ? LIMIT 1".format(self.label, key)
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(exec_str, [value])
            row = cursor.fetchone()
            description = cursor.description
        if not row:
            return None
        columns = [column[0] for column in description]
        return pandas.Series(row, index=columns)

    def close(self):
        pass