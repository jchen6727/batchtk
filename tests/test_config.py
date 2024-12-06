from batchtk.runtk import RunConfig
import pytest
import os
from collections import namedtuple
from batchtk.runtk.dispatchers import Dispatcher, INETDispatcher, UNIXDispatcher
from batchtk import runtk
from batchtk.runtk.submits import SHSubmit, SHSubmitSOCK, SHSubmitSFS
import json
Config = namedtuple('Config', ['initial', 'update', 'result'])
CONFIGS = [
    Config(
        [{'a': {'b': {'c': False}}}],
        [['a.b.c', True]],
        {'a': {'b': {'c': True}}}
    ),
    Config(
        [{'a': {'b': {'c': False}}}, ['d.e.f', False]],
        [['a', 'b', 'c', True], ['d', 'e', 'f', True]],
        {'a': {'b': {'c': True}}, 'd': {'e': {'f': True}}}
    )
]

class TestCONFIGS:
    @pytest.fixture(params=CONFIGS)
    def setup(self, request):
        cfg = RunConfig(*request.param.initial)
        return namedtuple('Setup', ['cfg', 'update', 'result'])(cfg, request.param.update, request.param.result)

    def test_init(self, setup):
        cfg = setup.cfg
        cfg.update(*setup.update)
        print(json.dumps(cfg))
        print(cfg == setup.result)
