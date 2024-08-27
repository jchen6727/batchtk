import pytest
import os
from batchtk import runtk
from batchtk.runtk.dispatchers import INETDispatcher, UNIXDispatcher
from batchtk.runtk.submits import SHSubmitSOCK
from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER

from batchtk.utils import get_exports#TODO implement a more universal get_port_info
import logging
import json
from collections import namedtuple
from header import TEST_ENVIRONMENT


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
handler = logging.FileHandler('test_job.log')

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
        submit.update_templates(command='python runner_scripts/rosenbrock_py.py')
        kwargs = {
            'config': config,
            'label': "trial",
            'tid': "{}{}".format(config['x0'], config['x1']),
            'dispatcher_constructor': request.param.Dispatcher,
            'project_path': os.getcwd(),
            'output_path': "output",
            'submit': submit,
        }
        return kwargs

    def test_trial(self, setup):
        kwargs = setup
        results = trial(**kwargs)
        for key in kwargs['config']:
            assert key in results
        for key in ['x0', 'x1']:
            assert kwargs['config'][key] == results[key]
        assert results['fx'] == rosenbrock(kwargs['config']['x0'], kwargs['config']['x1'])
        assert os.path.exists(results['file'])




