from pubtk.runtk import SocketRunner
import os
import sys
print(os.getpid())

runner = SocketRunner()
try:
    runner.connect() # connect to dispatcher
    print("connected to dispatcher")
    result = runner.mappings['intvalue'] + runner.mappings['fltvalue']
    runner.send(str(result))
#    data = runner.recv()
#    print(data)
    runner.close()
except Exception as e:
    runner.close()
    print(e)
    sys.exit()