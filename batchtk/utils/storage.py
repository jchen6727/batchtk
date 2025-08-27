class SQLStorage(object):# Use as TrialTable or Table object nomenclature to avoid confusion with logger
    def __init__(self):
        self.path = None

    def init_db(self): # initializes the database
        pass

    def get_schema(self): # get the schema of the storage
        pass

    def add_columns(self, schema: dict): # add new columns to storage
        pass

    def insert(self, entry: dict):#replace log with "insert" // see below
        pass

    def close(self):
        pass

class SQLiteStorage(SQLStorage): #SQLiteTable...
    def __init__(self,
                 label: str ='trials',
                 path: str = '.',
                 entries: Optional[Dict|List] = None,
                 add_trial_metadata: bool = True):
        from filelock import FileLock
        import sqlite3
        super().__init__()
        path = get_path(path)
        os.makedirs(path, exist_ok=True)
        self.label = label
        if entries is None:
            self.entries = dict()
        elif isinstance(entries, (list, tuple)) and all(isinstance(entry, str) for entry in entries):
            self.entries = {entry: 'TEXT' for entry in entries}
        else:
            self.entries = entries
        assert isinstance(self.entries, dict)
        if add_trial_metadata:
            self.entries = {'trial_path': 'TEXT', 'trial_label': 'TEXT'} | self.entries # can do TEXT NOT NULL or TEXT DEFAULT None for missing insertions...
        self.path = "{}/{}.sqlite.db".format(path, label)
        self._connect = sqlite3.connect
        self._lock = FileLock("{}.lock".format(self.path))
        self._oe = sqlite3.OperationalError
        self.init_db()

    def get_schema(self):
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info({})".format(self.label))
            data = cursor.fetchall()
            conn.close()
        schema = {column[1]: column[2] for column in data} # not set operation,
        return schema

    def init_db(self):
        if os.path.exists(self.path): # check that the db is appropriate if it exists ---
            schema = self.get_schema() # after init, check schema only once, then treat entries.keys as the relevant metadata
            if set(self.entries.items()) <= set(schema.items()):
                self.entries = schema # update entries to the current schema, if it is a subset of the expected entries
                return
            else:
                raise ValueError(f"database at path {self.path} expects different entries than given: schema {schema} conflicts with entries {self.entries}")
        exec_str = "id INTEGER PRIMARY KEY AUTOINCREMENT, {}".format(','.join(["[{}] {}".format(k, v) for k, v in self.entries.items()]))
        exec_str = "CREATE TABLE IF NOT EXISTS {} ({})".format(self.label, exec_str)
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str)
            conn.commit()
            conn.close()

    def insert(self, entries: dict): # record/add/insert/save
        if not set(entries.keys()) <= set(self.entries.keys()):
            raise ValueError(f"entries keys exceed expected keys: {entries.keys()} != {self.entries.keys()}")
        keys, vals = zip(*entries.items())
        exec_str = "INSERT INTO {} ([{}]) VALUES ({})".format(self.label, '],['.join(keys), ','.join(['?'] * len(vals)))
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str, vals)
            conn.commit()
            conn.close()

    def add_columns(self, columns: list | tuple | dict) -> list[tuple[str, Exception]]:
        #clarify nomenclature, header implies creation of metadata for a DB
        # compare columns against existing self.entries ---
        if isinstance(columns, (list, tuple)):
            new_columns = {column: 'TEXT' for column in columns if column not in self.entries.keys()}
        if isinstance(columns, dict):
            new_columns = {key: value for key, value in columns.items() if key not in self.entries.keys()}
        exec_strs = ["ALTER TABLE {} ADD COLUMN [{}] {}".format(self.label, new_column, new_value)
                     for new_column, new_value in new_columns.items()]
        oe = []
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            for new_column, exec_str in zip(new_columns.keys(), exec_strs):
                try:
                    cursor.execute(exec_str)
                    oe.append( (new_column, None) )
                except self._oe as e:
                    oe.append( (new_column, e) )
            conn.commit()
            conn.close()
        self.entries = self.get_schema()
        return oe


    def to_df(self):
        exec_str = "SELECT * FROM {}".format(self.label)
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str)
            rows = cursor.fetchall()
            description = cursor.description
            conn.close()
        columns = [column[0] for column in description]
        df = pandas.DataFrame(rows, columns=columns)
        return df

    def find(self, column: str, value: Any):
        if column not in self.entries:
            raise ValueError(f"column {column} not in entries: {self.entries}")
        exec_str = "SELECT * FROM {} WHERE {} = ?".format(self.label, column)
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str, [value])
            rows = cursor.fetchall()
            description = cursor.description
            conn.close()
        if not rows:
            return None
        columns = [column[0] for column in description]
        df = pandas.DataFrame(rows, columns=columns)
        return df

    def close(self):
        os.remove(self._lock.lock_file)
        self._lock = None