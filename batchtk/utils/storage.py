import os, pandas, numpy, sqlite3
import numpy as np
from batchtk.utils.misc import expand_path

class SQLStorage(object):# Use as TrialTable or Table object nomenclature to avoid confusion with logger
    def __init__(self):
        self.path = None

    def init_db(self): # initializes the database
        pass

    def read_schema(self): # get the schema of the storage
        pass

    def add_columns(self, schema: dict): # add new columns to storage
        pass

    def insert(self, entry: dict):#replace log with "insert" // see below
        pass

    def close(self):
        pass

### handle the serialization of numpy objects with global adapter registration...
sqlite3.register_adapter(np.integer, int)
sqlite3.register_adapter(np.floating, float)
sqlite3.register_adapter(np.bool_, int)


class SQLiteStorage(SQLStorage): #SQLiteTable...
    _DEFAULT_TYPE_MAP = {
        numpy.int64: "INTEGER",
        numpy.float64: "REAL",
        numpy.bool_: "INTEGER",
        bool: "INTEGER",
        int: "INTEGER",
        float: "REAL",
        str: "TEXT",
        bytes: "BLOB",
    }
    _DEFAULT_INFERENCE_RULES = {
        # Match specific, common types first for performance
        lambda v: "INTEGER" if type(v) in (int, bool) else None,
        lambda v: "REAL" if type(v) is float else None,
        lambda v: "TEXT" if type(v) is str else None,
        lambda v: "BLOB" if type(v) is bytes else None,
        # Fall back to robust isinstance() checks for entire hierarchies
        lambda v: "INTEGER" if isinstance(v, np.integer) else None,
        lambda v: "REAL" if isinstance(v, np.floating) else None,
        lambda v: "BLOB" if isinstance(v, np.ndarray) else None,
    ]

    def __init__(self,
                 label: str ='trials',
                 directory: str = '.',
                 filename: str = None,
                 schema: dict | list = None,
                 default_type: str= 'TEXT',
                 timeout: int =30,
                 ):
        ## handle the serialization of numpy objects
        super().__init__()
        directory = expand_path(directory)
        os.makedirs(directory, exist_ok=True)
        self.label = label
        if schema is None:
            self.schema = dict()
        elif isinstance(schema, (list, tuple)) and all(isinstance(column, str) for column in schema):
            self.schema = {column: default_type for column in schema}
        else:
            self.schema = schema
        assert isinstance(self.schema, dict)
        filename = filename or "{}.sqlite.db".format(label)
        self.path = "{}/{}".format(directory, filename)
        self.timeout = timeout
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
        self._create_db()

    def _infer_type(self, value):
        typed =
    def insert(self, entry: dict, allow_schema_update: bool = True):
        #diff = entry.keys() - self.schema.keys() #unordered
        if allow_schema_update:
            diff = {key: entry[key] for key in entry.keys() if key not in self.schema.keys()} #ordered

        if diff and allow_schema_update: # update the schema, then resync
            self.add_columns(diff)
        # record/add/insert/save
        if diff and not allow_schema_update:
            raise ValueError(f"entry keys {diff} do not exist in the db schema and allow_schema_update set to False.")
        keys, vals = zip(*entry.items())
        exec_str = "INSERT INTO {} ([{}]) VALUES ({})".format(self.label, '],['.join(keys), ','.join(['?'] * len(vals)))
        try:
            with self._wal_connect() as conn:
                cursor = conn.cursor()
                cursor.execute(exec_str, vals)
                conn.commit()
        except Exception as e:
            raise self._oe("inserting entry {} with exec_str {} failed with exception: {}".format(entry, exec_str, e))

    def add_columns(self, columns: list | tuple | dict) -> list[tuple[str, Exception]]:
        #clarify nomenclature, header implies creation of metadata for a DB
        # compare columns against existing self.schema ---
        if isinstance(columns, (list, tuple)):
            new_columns = {column: self.default_type for column in columns if column not in self.schema.keys()}
        if isinstance(columns, dict):
            check_columns = self.schema.keys() & columns.keys()
            if not all(self.schema[key] == columns[key] for key in check_columns):
                raise ValueError(f"columns dict provided {columns} conflicts with schema of SQLiteStorage: {self.schema} != {columns}")
            new_columns = {key: value for key, value in columns.items() if key not in self.entries.keys()}
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

    def find(self, column: str, value):
        if column not in self.schema:
            raise ValueError(f"column {column} does not exist in the db schema: {self.schema}")
        exec_str = "SELECT * FROM {} WHERE {} = ?".format(self.label, column)
        with self._wal_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(exec_str, [value])
            rows = cursor.fetchall()
            description = cursor.description
        if not rows:
            return None
        columns = [column[0] for column in description]
        df = pandas.DataFrame(rows, columns=columns)
        return df

    def close(self):
        pass



    What is a round-trip()

    serialization and deserialization