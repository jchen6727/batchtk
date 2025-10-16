from pymoo.problems.multi.mw import MW4, MW8, MW14
from pymoo.core.problem import Problem

def get_mw4(n_var, n_obj, *args, **kwargs):
    return MW4(n_var=n_var, n_obj=n_obj, *args, **kwargs)

def evaluate(problem: Problem, X, *args, **kwargs):
    out = {}
    problem._evaluate(X=X, out=out, *args, **kwargs)
    return out

def get_front(problem: Problem, *args, **kwargs):
    return problem._calc_pareto_front(*args, **kwargs)


