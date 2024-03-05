from pubtk.runtk import SocketRunner
import os, json

print(os.getpid())

runner = SocketRunner()

mappings = json.dumps(runner.mappings)

runner.connect()
runner.send(mappings)
print(mappings)
runner.close()