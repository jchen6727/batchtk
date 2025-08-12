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

result_out = OUTPUT_PATH(__file__)
log_out = LOG_PATH(__file__)

Job = namedtuple('Job', ['Dispatcher', 'Submit', 'config'])

#JOBS = [
#        Job(INETDispatcher, SHSubmitSOCK),
#        Job(UNIXDispatcher, SHSubmitSOCK)
#        ]

CONFIGS = [
        {'x0': 0, 'x1': 1}, {'x0': 1, 'x1': 0}
        ]

TRIALS = [Job(INETDispatcher, SHSubmitSOCK, config) for config in CONFIGS]

A = 1
def rosenbrock(x0, x1):
    return 100 * (x1 - x0**2)**2 + (A - x0)**2

storage = SQLiteStorage(entries= ('x0', 'x1', 'fx', 'path', 'label'), path=result_out)
logger = ScriptLogger(file_out=log_out)

class TestTRAILS:
    @pytest.fixture(params=TRIALS)
    def setup(self, request):
        config = request.param.config
        config['path'] = PATH_POINTER
        config['label'] = LABEL_POINTER
        kwargs = {
            'config': config,
            'label': "trial",
            'tid': "{}{}".format(config['x0'], config['x1']),
            'dispatcher_constructor': request.param.Dispatcher,
            'project_path': __file__.rsplit('/', 1)[0],
            'output_path': OUTPUT_PATH(__file__),
            'submit_constructor': request.param.Submit,
            'dispatcher_kwargs': None,
            'submit_kwargs': {'command': 'python runner_scripts/rosenbrock0_py.py'},
            'interval': 1,
            'data_storage': storage,
            'debug_log': logger,
            'report': ('path', 'data'),
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




"""
    Run a single trial:
    config: dict - parameter configuration for the trial (variables to be passed by the dispatcher to the receiving script)
    label: str - label for a set of trials (see trials)
    tid: str or int - trial id unique to this single trial
    dispatcher_constructor: callable - dispatcher class to be used for this trial
    project_path: str - path to the project directory
    output_path: str - path to the output directory
    submit_constructor: callable - submit class to be used for this trial
    dispatcher_kwargs: dict - kwargs to be passed to the dispatcher constructor
    submit_kwargs: dict - kwargs to be passed to the submit templates
    interval: int - interval for the dispatcher to check for messages
    data_storage: Storage - data storage for trial results
    debug_log: Logger - logger used for debug output
    report: tuple - options/order (left -> right update calls) for the data to be returned
    cleanup: bool or list/tuple - (True -> clean all files) clean up associated trial handles after a trial is completed.
    check_storage: bool - use the passed data_storage as a checkpoint for the trial, if trial data exists with a matching <label>_<tid>, then the trial is skipped and the stored data is pulled from check_storage.
"""
