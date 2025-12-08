import pytest
from batchtk.algos.pymoo_utils import get_algorithm, _get_algo
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.brkga import BRKGA
from pymoo.algorithms.soo.nonconvex.nelder import NelderMead
from pymoo.algorithms.soo.nonconvex.pattern import PatternSearch
from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
from pymoo.algorithms.soo.nonconvex.es import ES
from pymoo.algorithms.soo.nonconvex.sres import SRES
from pymoo.algorithms.soo.nonconvex.isres import ISRES
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.algorithms.soo.nonconvex.nrbo import NRBO
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.rnsga2 import RNSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.unsga3 import UNSGA3
from pymoo.algorithms.moo.rnsga3 import RNSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.ctaea import CTAEA
from pymoo.algorithms.moo.rvea import RVEA
from pymoo.algorithms.moo.spea2 import SPEA2

from collections import namedtuple

Algo = namedtuple('Algo', ['name', 'algo', 'path'])
algos = [
    Algo('GA', GA, ('soo', 'nonconvex', 'ga', 'GA')),
    Algo('DE', DE, ('soo', 'nonconvex', 'de', 'DE')),
    Algo('BRKGA', BRKGA, ('soo', 'nonconvex', 'brkga', 'BRKGA')),
    Algo('NelderMead', NelderMead, ('soo', 'nonconvex', 'nelder', 'NelderMead')),
    Algo('PatternSearch', PatternSearch, ('soo', 'nonconvex', 'pattern', 'PatternSearch')),
    Algo('CMAES', CMAES, ('soo', 'nonconvex', 'cmaes', 'CMAES')),
    Algo('ES', ES, ('soo', 'nonconvex', 'es', 'ES')),
    Algo('SRES', SRES, ('soo', 'nonconvex', 'sres', 'SRES')),
    Algo('ISRES', ISRES, ('soo', 'nonconvex', 'isres', 'ISRES')),
    Algo('PSO', PSO, ('soo', 'nonconvex', 'pso', 'PSO')),
    Algo('NRBO', NRBO, ('soo', 'nonconvex', 'nrbo', 'NRBO')),
    Algo('NSGA2', NSGA2, ('moo', 'nsga2', 'NSGA2')),
    Algo('RNSGA2', RNSGA2, ('moo', 'rnsga2', 'RNSGA2')),
    Algo('NSGA3', NSGA3, ('moo', 'nsga3', 'NSGA3')),
    Algo('UNSGA3', UNSGA3, ('moo', 'unsga3', 'UNSGA3')),
    Algo('RNSGA3', RNSGA3, ('moo', 'rnsga3', 'RNSGA3')),
    Algo('MOEAD', MOEAD, ('moo', 'moead', 'MOEAD')),
    Algo('CTAEA', CTAEA, ('moo', 'ctaea', 'CTAEA')),
    Algo('RVEA', RVEA, ('moo', 'rvea', 'RVEA')),
    Algo('SPEA2', SPEA2, ('moo', 'spea2', 'SPEA2')),
]

class TestJOBS:
    @pytest.mark.parametrize("algo", algos)
    def test_get_algo(self, algo):
        assert algo.algo == _get_algo(algo.path)

    def test_failed_get_algo(self):
        with pytest.raises(ImportError):
            _get_algo(('nonexistent', 'module', 'Algo'))
        with pytest.raises(AttributeError):
            _get_algo(('soo', 'nonconvex', 'ga', 'NonExistentAlgo'))