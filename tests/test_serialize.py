import pytest
import os
from header import TEST_ENVIRONMENT, LOG_PATH, CLEAN_OUTPUTS
from batchtk.runtk.dispatchers import Dispatcher
from batchtk.runtk.runners import get_class
from batchtk import runtk
from collections import namedtuple
import logging

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_PATH(__file__))

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

Job = namedtuple('Job', ['dispatcher', 'key', 'val'])
class TestEnv:
    @pytest.fixture(params=TEST_ENVIRONMENT.items())
    def setup(self, request):
        key, val = request.param[0], request.param[1]
        dispatcher = Dispatcher(label='test_serialize')
        dispatcher.update_env({key: val})
        logger.info("testing key: {} with {} value: {}".format(key, type(val).__name__, val))
        R = get_class()
        R._reinstance = True
        yield namedtuple('Setup', ['dispatcher', 'key', 'val', 'Runner'])(dispatcher, key, val, R)

    def test_env(self, setup):
        env = setup.dispatcher.env
        logger.info("dispatcher.env:\n{}".format(env))
        runner = setup.Runner(env=env)
        mappings = runner.get_mappings()
        logger.info("runner.mappings:\n{}".format(mappings))
        assert mappings[setup.key] == setup.val
        runner.close()
