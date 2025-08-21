import pytest
import os
from batchtk import runtk
from batchtk.runtk.dispatchers import INETDispatcher, UNIXDispatcher
from batchtk.runtk.submits import SHSubmitSOCK
from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER

from batchtk.utils import create_path, ScriptLogger, SQLiteStorage

import logging
import json
from collections import namedtuple
from header import TEST_ENVIRONMENT, LOG_PATH, OUTPUT_PATH, CLEAN_OUTPUTS
from numpy import random
result_out = OUTPUT_PATH(__file__)
log_out = LOG_PATH(__file__)

Job = namedtuple('Job', ['id', 'Dispatcher', 'Submit', 'config'])

SEED = 0
MIN, MAX = -4, 6
NTRIALS = 20
#JOBS = [
#        Job(INETDispatcher, SHSubmitSOCK),
#        Job(UNIXDispatcher, SHSubmitSOCK)
#        ]

CONFIGS = [
        {'x0': x0, 'x1': x1} for x0, x1 in
         random.default_rng(SEED).integers(MIN, MAX, (NTRIALS, 2))
        ]

TRIALS = [Job(id, INETDispatcher, SHSubmitSOCK, config) for id, config in enumerate(CONFIGS)]

A = 1
def rosenbrock(x0, x1):
    return 100 * (x1 - x0**2)**2 + (A - x0)**2

storage = SQLiteStorage(path=result_out)
logger = ScriptLogger(file_out=log_out)

class TestTRIALS:
    @pytest.fixture(params=TRIALS)
    def setup(self, request):
        config = request.param.config
        config['path'] = PATH_POINTER
        config['label'] = LABEL_POINTER
        kwargs = {
            'config': config,
            'label': "trial",
            'tid': "{}".format(request.param.id),
            'dispatcher_constructor': request.param.Dispatcher,
            'project_path': __file__.rsplit('/', 1)[0],
            'output_path': OUTPUT_PATH(__file__),
            'submit_constructor': request.param.Submit,
            'dispatcher_kwargs': None,
            'submit_kwargs': {'command': 'python runner_scripts/rosenbrock0_py.py'},
            'interval': 1,
            'data_storage': storage,
            'debug_log': logger,
            'report': ('path', 'config', 'data'),
            'cleanup': True,
            'check_storage': True,
        }
        yield kwargs
        #os.rmdir(create_path(kwargs['project_path'], kwargs['output_path']))

    def test_trial(self, setup):
        kwargs = setup
        results = trial(**kwargs)
        for key in kwargs['config']:
            assert key in results
        for key in ['x0', 'x1']:
            assert kwargs['config'][key] == results[key]
        assert results['fx'] == rosenbrock(kwargs['config']['x0'], kwargs['config']['x1'])
        print(results)


