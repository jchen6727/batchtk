from batchtk.runtk import get_runner
import os
import sys
import json

"""
The rosenbrock minimum is at (A, A**2), where rosenbrock(A, A**2) = 0
"""
A = 1

print("starting process: {}".format(os.getpid()))

def rosenbrock(x0, x1):
    return 100 * (x1 - x0**2)**2 + (A - x0)**2

runner = get_runner()
print("runner id: {}".format(id(runner)))
mappings = {'x0': A, 'x1': A**2}
mappings.update(runner.get_mappings())

inputs = {key: mappings[key] for key in ('x0', 'x1')}

if 'path' in mappings and 'label' in mappings:
    file = "{}/{}.txt".format(mappings['path'], mappings['label'])
    mappings['file'] = file

fx = rosenbrock(mappings['x0'], mappings['x1'])
#results = json.dumps({**mappings, 'fx': fx})
results = json.dumps({**inputs, 'fx': fx})


print(results)
with get_runner() as runner:
    print("communication runner id: {}".format(id(runner)))
    runner.send(results)

if 'file' in mappings:
    file = "{}/{}.txt".format(mappings['path'], mappings['label'])
    print("writing results to file: {}".format(file))
    with open(file, 'w') as fptr:
        fptr.write(results)

