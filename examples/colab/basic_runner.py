from pubtk.runtk import Runner
import os, sys, json

print(os.getpid())

runner = Runner()

mappings = json.dumps(runner.mappings)

print(mappings)