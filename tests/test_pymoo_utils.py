import pytest
from batchtk.algos.pymoo_utils import get_algorithm, _get_algo
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.spea2 import SPEA2
from pymoo.algorithms.soo.nonconvex.pso import PSO

from collections import namedtuple

algos = {
    
}
class TestJOBS:
    @pytest.fixture(params=JOBS)
    def setup(self, request):
        _Submit = request.param.Submit
        submit = _Submit()
        _Dispatcher = request.param.Dispatcher
        uid = str(uuid.uuid4())
        key_uid = 'j_'+uid[:4]
        env = {key_uid: uid}
        dispatcher = _Dispatcher(project_path='./runner_scripts',
                                 output_path=OUTPUT_PATH(__file__),
                                              submit=submit,
                                              env=env,
                                              label='test' + _Dispatcher.__name__ + _Submit.__name__)
        yield namedtuple('Setup', ['dispatcher', 'submit', 'env'])(dispatcher, submit, env)
        #CLEAN_OUTPUTS(dispatcher) not good for



def test_get_algo_valid():
    """Test that a valid path returns the correct algorithm class."""
    path = ('soo', 'nonconvex', 'pso', 'PSO')
    algorithm_class = _get_algo(path)
    assert algorithm_class == PSO

def test_get_algo_invalid_module():
    """Test that an invalid module path raises an ImportError."""
    path = ('foo', 'bar', 'Baz')
    with pytest.raises(ImportError):
        _get_algo(path)

def test_get_algo_invalid_attribute():
    """Test that an invalid algorithm name raises an AttributeError."""
    path = ('soo', 'nonconvex', 'pso', 'InvalidAlgo')
    with pytest.raises(AttributeError):
        _get_algo(path)
