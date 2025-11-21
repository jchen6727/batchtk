"""
Tests for batchtk/utils/storage.py SQLiteStorage class.

Covers:
1. Multithreading handling (concurrent inserts, reads)
2. New datatype entries (type inference and registration)
3. Pickle serialization/deserialization of the instance
"""

import pytest
import os
import pickle
import tempfile
import shutil
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import namedtuple

from batchtk.utils.storage import SQLiteStorage


class TestSQLiteStorageMultithreading:
    """Test concurrent access to SQLiteStorage."""

    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for test databases."""
        tmpdir = tempfile.mkdtemp(prefix='test_sqlstorage_')
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.fixture
    def storage(self, storage_dir):
        """Create a SQLiteStorage instance for testing."""
        storage = SQLiteStorage(
            label='test_mt',
            directory=storage_dir,
            filename='test_multithread.sqlite.db',
            schema={'trial_id': 'INTEGER', 'value': 'REAL'},
            timeout=30
        )
        yield storage
        storage.close()

    def test_concurrent_inserts(self, storage):
        """Test that multiple threads can insert concurrently without errors."""
        n_threads = 10
        n_inserts_per_thread = 20

        def insert_entries(thread_id):
            results = []
            for i in range(n_inserts_per_thread):
                entry = {
                    'trial_id': thread_id * 1000 + i,
                    'value': float(thread_id) + i * 0.01
                }
                storage.insert(entry)
                results.append(entry['trial_id'])
            return results

        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = {executor.submit(insert_entries, tid): tid for tid in range(n_threads)}
            all_inserted = []
            for future in as_completed(futures):
                all_inserted.extend(future.result())

        # Verify all inserts succeeded
        assert len(all_inserted) == n_threads * n_inserts_per_thread

        # Verify data integrity via to_df
        df = storage.to_df()
        assert len(df) == n_threads * n_inserts_per_thread

    def test_concurrent_reads_and_writes(self, storage):
        """Test mixed read/write operations across threads."""
        n_threads = 8

        def mixed_operations(thread_id):
            results = []
            for i in range(10):
                entry = {'trial_id': thread_id * 100 + i, 'value': float(i)}
                storage.insert(entry)
                results.append(('insert', entry['trial_id']))

                # Attempt to find a previously inserted entry
                if i > 0:
                    found = storage.find('trial_id', thread_id * 100 + i - 1)
                    results.append(('find', found is not None))
            return results

        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = [executor.submit(mixed_operations, tid) for tid in range(n_threads)]
            for future in as_completed(futures):
                result = future.result()
                # Verify finds succeeded (at least some should have)
                finds = [r for r in result if r[0] == 'find']
                assert any(f[1] for f in finds), "At least some finds should succeed"

    def test_concurrent_schema_updates(self, storage_dir):
        """Test that concurrent schema updates (adding columns) are handled safely."""
        storage = SQLiteStorage(
            label='test_schema_mt',
            directory=storage_dir,
            filename='test_schema_mt.sqlite.db',
            schema=None,  # Start with no schema
            timeout=30
        )

        def insert_with_new_column(thread_id):
            # Each thread tries to add entries with a unique column
            col_name = f'thread_{thread_id}_col'
            entries = []
            for i in range(5):
                entry = {'base_id': thread_id * 100 + i, col_name: i * 1.5}
                storage.insert(entry, allow_schema_updates=True)
                entries.append(entry)
            return col_name, entries

        n_threads = 5
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = [executor.submit(insert_with_new_column, tid) for tid in range(n_threads)]
            results = [f.result() for f in as_completed(futures)]

        # Verify all columns were added
        schema = storage.read_schema()
        for col_name, _ in results:
            assert col_name in schema, f"Column {col_name} should be in schema"

        storage.close()


class TestSQLiteStorageDatatypes:
    """Test type inference and registration for various datatypes."""

    @pytest.fixture
    def storage_dir(self):
        tmpdir = tempfile.mkdtemp(prefix='test_sqlstorage_dt_')
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.fixture
    def storage(self, storage_dir):
        storage = SQLiteStorage(
            label='test_datatypes',
            directory=storage_dir,
            filename='test_datatypes.sqlite.db',
            schema=None,
            timeout=30
        )
        yield storage
        storage.close()

    @pytest.mark.parametrize("value,expected_type", [
        (42, "INTEGER"),
        (3.14159, "REAL"),
        ("hello world", "TEXT"),
        (True, "INTEGER"),
        (False, "INTEGER"),
    ])
    def test_basic_type_inference(self, storage, value, expected_type):
        """Test that basic Python types are correctly inferred."""
        col_name = f'col_{type(value).__name__}'
        entry = {'id_col': 1, col_name: value}
        storage.insert(entry, allow_schema_updates=True)

        schema = storage.read_schema()
        assert col_name in schema
        assert schema[col_name] == expected_type

    @pytest.mark.parametrize("value,expected_type", [
        (np.int64(42), "INTEGER"),
        (np.float64(3.14), "REAL"),
        (np.int32(100), "INTEGER"),
        (np.float32(2.5), "REAL"),
    ])
    def test_numpy_type_inference(self, storage, value, expected_type):
        """Test that numpy types are correctly inferred via type rules."""
        col_name = f'col_{type(value).__name__}'
        entry = {'id_col': 1, col_name: value}
        storage.insert(entry, allow_schema_updates=True)

        schema = storage.read_schema()
        assert col_name in schema
        assert schema[col_name] == expected_type

    def test_pblob_fallback_for_complex_types(self, storage):
        """Test that complex types fall back to PBLOB (pickled blob)."""
        complex_values = [
            ('list_col', [1, 2, 3, 4, 5]),
            ('dict_col', {'nested': {'key': 'value'}}),
            ('tuple_col', (1, 2, 'three')),
            ('set_col', {1, 2, 3}),
            ('ndarray_col', np.array([1, 2, 3])),
        ]

        for col_name, value in complex_values:
            entry = {'id_col': hash(col_name) % 10000, col_name: value}
            storage.insert(entry, allow_schema_updates=True)

        schema = storage.read_schema()
        for col_name, _ in complex_values:
            assert col_name in schema
            assert schema[col_name] == 'PBLOB', f"{col_name} should be PBLOB"

    def test_pblob_roundtrip(self, storage_dir):
        """Test that PBLOB values survive insert/retrieve roundtrip."""
        storage = SQLiteStorage(
            label='test_pblob_rt',
            directory=storage_dir,
            filename='test_pblob_rt.sqlite.db',
            schema=None,
            timeout=30,
            default_type='PBLOB'
        )

        test_data = {
            'trial_id': 1,
            'list_val': [1, 2, 3, {'nested': True}],
            'dict_val': {'a': 1, 'b': [2, 3]},
            'array_val': np.array([[1, 2], [3, 4]]),
        }

        storage.insert(test_data, allow_schema_updates=True)
        result = storage.find('trial_id', 1)

        assert result is not None
        assert result['list_val'] == test_data['list_val']
        assert result['dict_val'] == test_data['dict_val']
        np.testing.assert_array_equal(result['array_val'], test_data['array_val'])

        storage.close()

    def test_text_fallback_mode(self, storage_dir):
        """Test TEXT fallback mode for unknown types."""
        storage = SQLiteStorage(
            label='test_text_fallback',
            directory=storage_dir,
            filename='test_text_fallback.sqlite.db',
            schema=None,
            timeout=30,
            default_type='TEXT'
        )

        # Custom class that will be converted to TEXT
        class CustomObj:
            def __init__(self, val):
                self.val = val
            def __str__(self):
                return f"CustomObj({self.val})"

        entry = {'trial_id': 1, 'custom': CustomObj(42)}
        storage.insert(entry, allow_schema_updates=True)

        schema = storage.read_schema()
        assert schema['custom'] == 'TEXT'

        storage.close()

    def test_type_map_registration(self, storage):
        """Test that new types get registered in type_map after inference."""
        initial_type_map_size = len(storage.type_map)

        # Insert a numpy type that should trigger rule-based inference
        entry = {'trial_id': 1, 'np_val': np.int16(100)}
        storage.insert(entry, allow_schema_updates=True)

        # type_map should have grown
        assert len(storage.type_map) > initial_type_map_size
        assert np.int16 in storage.type_map


class TestSQLiteStoragePickleSerialization:
    """Test pickle serialization/deserialization of SQLiteStorage instances."""

    @pytest.fixture
    def storage_dir(self):
        tmpdir = tempfile.mkdtemp(prefix='test_sqlstorage_pickle_')
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_basic_pickle_roundtrip(self, storage_dir):
        """Test that SQLiteStorage can be pickled and unpickled."""
        storage = SQLiteStorage(
            label='test_pickle',
            directory=storage_dir,
            filename='test_pickle.sqlite.db',
            schema={'x': 'REAL', 'y': 'INTEGER'},
            timeout=30
        )

        # Insert some data
        storage.insert({'x': 1.5, 'y': 10})
        storage.insert({'x': 2.5, 'y': 20})

        # Pickle and unpickle
        pickled = pickle.dumps(storage)
        restored = pickle.loads(pickled)

        # Verify restored instance works
        assert restored.label == storage.label
        assert restored.path == storage.path
        assert restored.schema == storage.schema

        # Verify data access works
        df = restored.to_df()
        assert len(df) == 2

        # Verify new inserts work
        restored.insert({'x': 3.5, 'y': 30})
        df = restored.to_df()
        assert len(df) == 3

        storage.close()
        restored.close()

    def test_pickle_preserves_type_map(self, storage_dir):
        """Test that custom type registrations survive pickle roundtrip."""
        storage = SQLiteStorage(
            label='test_pickle_types',
            directory=storage_dir,
            filename='test_pickle_types.sqlite.db',
            schema=None,
            timeout=30
        )

        # Insert various types to populate type_map
        storage.insert({
            'int_col': 1,
            'float_col': 1.5,
            'str_col': 'test',
            'np_int': np.int64(42),
            'np_float': np.float64(3.14),
        }, allow_schema_updates=True)

        original_type_map = storage.type_map.copy()
        original_schema = storage.schema.copy()

        # Pickle roundtrip
        pickled = pickle.dumps(storage)
        restored = pickle.loads(pickled)

        # Verify type_map preserved
        assert restored.type_map == original_type_map
        assert restored.schema == original_schema

        storage.close()
        restored.close()

    def test_pickle_state_attributes_stripped(self, storage_dir):
        """Test that _state_attributes are properly stripped during pickle."""
        storage = SQLiteStorage(
            label='test_state_strip',
            directory=storage_dir,
            filename='test_state_strip.sqlite.db',
            schema=None,
            timeout=30
        )

        # Get the state that would be pickled
        state = storage.__getstate__()

        # Verify state attributes are stripped
        for attr in storage._state_attributes:
            if attr:  # Skip empty string
                assert attr not in state, f"{attr} should be stripped from pickle state"

        storage.close()

    def test_pickle_state_rebuilt_on_load(self, storage_dir):
        """Test that transient state is rebuilt after unpickling."""
        storage = SQLiteStorage(
            label='test_state_rebuild',
            directory=storage_dir,
            filename='test_state_rebuild.sqlite.db',
            schema={'value': 'REAL'},
            timeout=30
        )

        storage.insert({'value': 1.0})

        # Pickle and unpickle
        pickled = pickle.dumps(storage)
        restored = pickle.loads(pickled)

        # Verify _connect is available (should be sqlite3.connect)
        assert hasattr(restored, '_connect')
        assert restored._connect is not None

        # Verify _oe is available (should be sqlite3.OperationalError)
        assert hasattr(restored, '_oe')
        assert restored._oe is not None

        # Verify the restored instance can perform DB operations
        restored.insert({'value': 2.0})
        result = restored.find('value', 1.0)
        assert result is not None

        storage.close()
        restored.close()

    def test_pickle_to_file_and_back(self, storage_dir):
        """Test pickling to a file and loading back."""
        storage = SQLiteStorage(
            label='test_file_pickle',
            directory=storage_dir,
            filename='test_file_pickle.sqlite.db',
            schema={'trial_id': 'INTEGER', 'result': 'PBLOB'},
            timeout=30
        )

        # Insert complex data
        storage.insert({
            'trial_id': 1,
            'result': {'accuracy': 0.95, 'history': [0.5, 0.7, 0.9, 0.95]}
        })

        # Save to file
        pickle_path = os.path.join(storage_dir, 'storage.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(storage, f)

        # Load from file
        with open(pickle_path, 'rb') as f:
            restored = pickle.load(f)

        # Verify functionality
        result = restored.find('trial_id', 1)
        assert result is not None
        assert result['result']['accuracy'] == 0.95
        assert result['result']['history'] == [0.5, 0.7, 0.9, 0.95]

        storage.close()
        restored.close()

    def test_pickle_multiple_times(self, storage_dir):
        """Test that storage can be pickled multiple times."""
        storage = SQLiteStorage(
            label='test_multi_pickle',
            directory=storage_dir,
            filename='test_multi_pickle.sqlite.db',
            schema={'counter': 'INTEGER'},
            timeout=30
        )

        for i in range(3):
            storage.insert({'counter': i})

            # Pickle and restore
            pickled = pickle.dumps(storage)
            storage = pickle.loads(pickled)

            # Verify each iteration
            df = storage.to_df()
            assert len(df) == i + 1

        storage.close()

    def test_pickle_with_concurrent_access(self, storage_dir):
        """Test pickling while concurrent operations are happening."""
        storage = SQLiteStorage(
            label='test_concurrent_pickle',
            directory=storage_dir,
            filename='test_concurrent_pickle.sqlite.db',
            schema={'thread_id': 'INTEGER', 'value': 'REAL'},
            timeout=30
        )

        def worker(thread_id, storage_obj):
            for i in range(5):
                storage_obj.insert({'thread_id': thread_id, 'value': float(i)})
            return thread_id

        # Start with some data
        storage.insert({'thread_id': -1, 'value': 0.0})

        # Pickle mid-operation
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(worker, tid, storage) for tid in range(3)]

            # Pickle while threads are running
            pickled = pickle.dumps(storage)

            # Wait for all threads
            for f in as_completed(futures):
                f.result()

        # Restore and verify
        restored = pickle.loads(pickled)
        assert restored.path == storage.path

        # Both should see the final data (since they share the same DB file)
        df_original = storage.to_df()
        df_restored = restored.to_df()
        assert len(df_original) == len(df_restored)

        storage.close()
        restored.close()


class TestSQLiteStorageEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def storage_dir(self):
        tmpdir = tempfile.mkdtemp(prefix='test_sqlstorage_edge_')
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_schema_conflict_raises_error(self, storage_dir):
        """Test that conflicting schema raises ValueError."""
        # Create initial storage with schema
        storage1 = SQLiteStorage(
            label='test_conflict',
            directory=storage_dir,
            filename='test_conflict.sqlite.db',
            schema={'col1': 'INTEGER'},
            timeout=30
        )
        storage1.insert({'col1': 1})
        storage1.close()

        # Try to open with conflicting schema
        with pytest.raises(ValueError, match="conflicts"):
            SQLiteStorage(
                label='test_conflict',
                directory=storage_dir,
                filename='test_conflict.sqlite.db',
                schema={'col1': 'TEXT'},  # Conflict!
                timeout=30
            )

    def test_find_nonexistent_column_raises(self, storage_dir):
        """Test that finding by nonexistent column raises ValueError."""
        storage = SQLiteStorage(
            label='test_find_error',
            directory=storage_dir,
            filename='test_find_error.sqlite.db',
            schema={'existing_col': 'INTEGER'},
            timeout=30
        )

        with pytest.raises(ValueError, match="does not exist"):
            storage.find('nonexistent_col', 1)

        storage.close()

    def test_insert_without_schema_update_raises(self, storage_dir):
        """Test that inserting unknown columns without allow_schema_updates raises."""
        storage = SQLiteStorage(
            label='test_no_update',
            directory=storage_dir,
            filename='test_no_update.sqlite.db',
            schema={'known_col': 'INTEGER'},
            timeout=30
        )

        with pytest.raises(ValueError, match="do not exist"):
            storage.insert({'known_col': 1, 'unknown_col': 2}, allow_schema_updates=False)

        storage.close()

    def test_empty_db_operations(self, storage_dir):
        """Test operations on empty database."""
        storage = SQLiteStorage(
            label='test_empty',
            directory=storage_dir,
            filename='test_empty.sqlite.db',
            schema={'col1': 'INTEGER'},
            timeout=30
        )

        # to_df on empty should return empty DataFrame
        df = storage.to_df()
        assert len(df) == 0

        # find on empty should return None
        result = storage.find('col1', 1)
        assert result is None

        storage.close()
