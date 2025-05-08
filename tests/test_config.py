from batchtk.runtk import RunConfig
import pytest
from collections import namedtuple
import numpy
import json
Config = namedtuple('Config', ['initial', 'update', 'result'])
# the first entry is what the RunConfig looks like initially
# the second entry is what update string is called
# the third entry is what we expect the RunConfig to look like after the update result
CONFIGS = [
    Config(
        [{'a': {'b': {'c': False}}}],
        [['a.b.c', True]],
        {'a': {'b': {'c': True}}},
    ),
    Config(
        [{'a': {'b': {'c': False}}}, ['d.e.f', False]],
        [['a', 'b', 'c', True], ['d', 'e', 'f', True]],
        {'a': {'b': {'c': True}}, 'd': {'e': {'f': True}}}
    ),
    Config(
        [{'x': [False, False, False]}],
        [['x.1', True]],
        {'x': [False, True, False]}
    ),
    Config(
        [{'x': numpy.zeros(5)}],
        [['x.1', 1]],
        {'x': numpy.array([0., 1., 0., 0., 0.])}
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
        print(cfg.__dict__)
        assert str(cfg.__dict__) == str(setup.result)
