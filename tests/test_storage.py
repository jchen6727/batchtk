from batchtk.utils.storage import SQLiteStorage
from numpy import random, arange, hstack
import pytest
from collections import namedtuple


SEED = 0
NCOL = 5
NROW = 10
MIN = -5
MAX =  5

COLUMNS = ['id'] + ["column{}".format(val) for val in range(5)]
ENTRIES = random.default_rng(SEED).integers(MIN, MAX, (NROW, NCOL))
ID = arange(0, NROW).reshape(-1, 1)
ENTRIES = hstack([ID, ENTRIES])


class TestStorage:
    @pytest.fixture(params=ENTRIES)
    def setup(self, request):
        test = namedtuple('test', ['storage', 'entry'])
        storage = SQLiteStorage(label='trials', directory='.',
                                filename='test_storage.sqlite.db',
                                schema=None, timeout=30) # test without pre-defined schema
        yield test(storage, {key: val for key, val in zip(COLUMNS, request.param)})

    def test_storage(self, setup):
        storage = setup.storage
        entry = setup.entry
        storage.insert(entry)
        check = storage.find(column='id', value=entry['id'])
        print(check)




