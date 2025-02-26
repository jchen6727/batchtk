import pytest
import os
from batchtk import runtk
from batchtk.runtk.dispatchers import INETDispatcher, UNIXDispatcher
from batchtk.runtk.submits import SHSubmitSOCK
from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER

from batchtk.utils import create_path
import logging
import json
from collections import namedtuple
from header import TEST_ENVIRONMENT, LOG_PATH, OUTPUT_PATH, CLEAN_OUTPUTS


Job = namedtuple('Job', ['Dispatcher', 'Submit', 'config'])

#JOBS = [
#        Job(INETDispatcher, SHSubmitSOCK),
#        Job(UNIXDispatcher, SHSubmitSOCK)
#        ]

CONFIGS = [
        {'x0': 0, 'x1': 1}, {'x0': 1, 'x1': 0}
        ]

TRIALS = [Job(INETDispatcher, SHSubmitSOCK, config) for config in CONFIGS]

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_PATH(__file__))

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

A = 1
def rosenbrock(x0, x1):
    return 100 * (x1 - x0**2)**2 + (A - x0)**2
class TestTRAILS:
    @pytest.fixture(params=TRIALS)
    def setup(self, request):
        config = request.param.config
        config['path'] = PATH_POINTER
        config['label'] = LABEL_POINTER
        submit = request.param.Submit()
        submit.update_templates(command='python runner_scripts/rosenbrock0_py.py')
        kwargs = {
            'config': config,
            'label': "trial",
            'tid': "{}{}".format(config['x0'], config['x1']),
            'dispatcher_constructor': request.param.Dispatcher,
            'project_path': __file__.rsplit('/', 1)[0],
            'output_path': OUTPUT_PATH(__file__),
            'submit': submit,
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
        assert os.path.exists(results['file'])





