import os, pandas, numpy, sqlite3, io, pickle
import numpy
from typing import Any
from batchtk.utils.misc import expand_path
from batchtk.utils.serializer import SQLiteTypeRule

from collections import namedtuple

class Storage(object):
    def __init__(self):
        pass

    def insert(self, entry: dict):#replace log with "insert" // see below
        pass

    def find(self, key, value):
        pass

    def close(self):
        pass
class SQLStorage(Storage):# Use as TrialTable or Table object nomenclature to avoid confusion with logger
    def __init__(self):
        super().__init__()
        self.path = None

    def init_db(self): # initializes the database
        pass

    def read_schema(self): # get the schema of the storage
        pass

    def add_columns(self, schema: dict): # add new columns to storage
        pass

    def insert(self, entry: dict):#replace log with "insert" // see below
        pass

    def find(self, key, value):
        pass

    def close(self):
        pass

### handle the serialization of numpy objects with global adapter registration...

### as far as I can tell, this clunky approach sits on the pareto front... no refactors for now.
SQLiteTypeRuleResult=namedtuple('SQLiteTypeRuleResult', ['type', 'adapter'])

### the bigger issue is that a TypeRuleResult must be paired with an adapter function
def _SQLiteINTEGERRule(val: Any) -> SQLiteTypeRuleResult | None:
    """return SQLiteTypeRuleResult("INTEGER", int) for all numpy integer types. else returns None, None"""
    return SQLiteTypeRuleResult("INTEGER", int) if isinstance(val, numpy.integer) else None, None

def _SQLiteREALRule(val: Any) -> SQLiteTypeRuleResult | None:
    """return SQLiteTypeRuleResult("REAL", float) for all numpy floating types. else returns None, None"""
    return SQLiteTypeRuleResult("REAL", float) if isinstance(val, numpy.floating) else None, None

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

class SQLiteStorage(SQLStorage): #SQLiteTable...
    # relevant for adding columns to schema


    # serves as the initial LUT for type inference
    # any key in _DEFAULT_TYPE_MAP is considered registered --- that is
    # an ADAPTER is registered for that type (and a CONVERTER if necessary)
    _DEFAULT_TYPE_MAP = { # serves as the initial LUT for type inference
        numpy.int64: "INTEGER",
        numpy.float64: "REAL",
        #numpy.bool_: "INTEGER", # if numpy themselves aren't going to figure out numpy.bool or numpy.bool_ then I'm not going to support it
        bool: "INTEGER",
        int: "INTEGER",
        float: "REAL",
        str: "TEXT",
    }

    _DEFAULT_TYPE_RULES= [
        SQLiteTypeRule(function=_SQLiteINTEGERRule, priority=0),
        SQLiteTypeRule(function=_SQLiteREALRule, priority=1),
    ]

    _DEFAULT_ADAPTERS = [
        (numpy.int64, int), # calls int on numpy.integer
        (numpy.float64, float), # calls float on numpy.floating
        #(numpy.bool_, int), # calls int on numpy.bool # so the preferred use is numpy.bool but randomly for 2 years this would break scripts.
        # https://github.com/numpy/numpy/issues/22021
        # so it will just have to default to PBLOB
    ]

    _DEFAULT_CONVERTERS = [
        ("PBLOB", _SQLitePBLOBConverter)
    ]

    def __init__(self,
                 label: str ='trials',
                 directory: str = '.',
                 filename: str = None,
                 schema: dict = None, # now dict instead of list/tuple 2/2 PBLOB default
                 default_type: str= 'PBLOB', #pickled BLOB or TEXT...
                 timeout: int =30,
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
        self.type_map = check_default(type_map, self._DEFAULT_TYPE_MAP)
        self.type_rules = check_default(type_rules, self._DEFAULT_TYPE_RULES)
        self.adapters = check_default(adapters, self._DEFAULT_ADAPTERS)
        self.converters = check_default(converters, self._DEFAULT_CONVERTERS)
        for py_type, adapter in self.adapters:
            sqlite3.register_adapter(py_type, adapter)
        for py_type, converter in self.converters:
            sqlite3.register_converter(py_type, converter)
        self._connect = sqlite3.connect
        self._oe = sqlite3.OperationalError
        self.default_type = default_type
        self.init_db()

    def _wal_connect(self, timeout=None):
        timeout = timeout or self.timeout
        conn = self._connect(self.path, timeout=timeout)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def read_schema(self):
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info({})".format(self.label))
            data = cursor.fetchall()
        schema = {column[1]: column[2] for column in data} # not set operation,
        return schema

    def _sync_schema(self):
        schema = self.read_schema()
        check_columns = self.schema.keys() & schema.keys()
        write_columns = {key: self.schema[key] for key in self.schema.keys() - schema.keys()}
        if not all(schema[key] == self.schema[key] for key in check_columns):
            raise ValueError(f"provided schema of SQLiteStorage conflicts datatypes with existing schema at path: {schema} != {self.schema}")
        if write_columns:
            self.add_columns(write_columns) # add things from self.schema that are not in the db
        self.schema.update(schema) # add things to self.schema that are in the db

    def _create_db(self):
        exec_str = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        if self.schema:
            exec_str += "id INTEGER PRIMARY KEY AUTOINCREMENT, {}".format(','.join(["[{}] {}".format(k, v) for k, v in self.schema.items()]))
        exec_str = "CREATE TABLE IF NOT EXISTS {} ({})".format(self.label, exec_str)
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(exec_str)
            conn.commit()

    def init_db(self):
        if os.path.exists(self.path): # new db
            self._sync_schema()
            return
        # fails if os.path.exists(self.path)...
        #for _type, adapter in self.adapters:
        #    sqlite3.register_adapter(_type, adapter)
        #for _type, converter in self.converters:
        #    sqlite3.register_converter(_type, converter)
        self._create_db()

    def insert(self, entry: dict, allow_schema_updates: bool = True):
        diff = entry.keys() - self.schema.keys() #unordered
        if allow_schema_updates:
            diff = {key: self.infer_and_register_type(entry[key]) for key in entry.keys() if key not in self.schema.keys()} #ordered
            self.add_columns(diff)
        # record/add/insert/save
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
        # LUT first
        inferred = self.type_map.get(val_type, None) ## essentially, if it hits on type_map, it is registered
        if inferred: return inferred
        # Rules next
        for rule in self.type_rules:
            inferred = rule(val)
            if inferred:
                self.type_map[val_type] = inferred.type
                sqlite3.register_adapter(val_type, inferred.adapter)
                return inferred.type
        # default (TEXT or PBLOB)
        if self.default_type == 'TEXT':
            self.type_map[type(val)] = "TEXT"
            sqlite3.register_adapter(type(val), str)
            return 'TEXT'
        if self.default_type == 'PBLOB':
            self.type_map[type(val)] = "PBLOB"
            sqlite3.register_adapter(type(val), _SQLitePBLOBAdapter)
            return 'PBLOB'
        raise(RuntimeError("no type inference for {}, and default_type {} not recognized".format(val, self.default_type)))

    def add_columns(self, columns: list | tuple | dict) -> list[tuple[str, Exception]]:
        #clarify nomenclature, header implies creation of metadata for a DB
        # compare columns against existing self.schema ---
        if isinstance(columns, (list, tuple)):
            new_columns = {column: self.default_type for column in columns if column not in self.schema.keys()}
        if isinstance(columns, dict):
            check_columns = self.schema.keys() & columns.keys()
            if not all(self.schema[key] == columns[key] for key in check_columns):
                raise ValueError(f"columns dict provided {columns} conflicts with schema of SQLiteStorage: {self.schema} != {columns}")
            new_columns = {key: value for key, value in columns.items() if key not in self.schema.keys()}
        exec_strs = ["ALTER TABLE {} ADD COLUMN [{}] {}".format(self.label, new_column, new_value)
                     for new_column, new_value in new_columns.items()]
        oe = []
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            for new_column, exec_str in zip(new_columns.keys(), exec_strs):
                try:
                    cursor.execute(exec_str)
                    oe.append( (new_column, None) )
                except self._oe as e:
                    oe.append( (new_column, e) )
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
        # using key and column interchangeably to generalize between
        # SQL, NoSQL and other storage paradigms.
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


"""
What is a round-trip()
serialization and deserialization
"""

# 100 lines of code for the predictable API --