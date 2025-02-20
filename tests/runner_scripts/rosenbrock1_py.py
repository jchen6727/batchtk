from batchtk.runtk import get_comm, RunConfig
import os
import sys
import json

comm = get_comm()
comm.connect()

A=1

def rosenbrock(x0, x1):
    return 100 * (x1 - x0**2)**2 + (A - x0)**2


cfg = RunConfig(
    {'x0': False, 'x1': False, 'path': False},
)

print(id(comm))
print(id(cfg._runner))

assert id(comm) == id(cfg._runner)
cfg.update(x0=1, x1=1)

x0, x1 = cfg['x0'], cfg['x1']

results = {
    'x0': x0,
    'x1': x1,
    'fx': rosenbrock(x0, x1)
}

print(results)












