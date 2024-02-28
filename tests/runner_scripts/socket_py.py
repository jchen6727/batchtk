from pubtk.runtk import SocketRunner
import os
import sys
import json
print("starting process: {}".format(os.getpid()))

runner = SocketRunner()
try:
    connection, peer_address = runner.connect() # connect to dispatcher
    print("connected to dispatcher:\n({},{})".format(connection, peer_address))
    print("received message from dispatcher: {}".format(runner.recv()))
    mappings = json.dumps(runner.mappings)
    result = runner.mappings['intvalue'] + runner.mappings['fltvalue']
    runner.send(mappings)
    print("sent mappings to dispatcher")
    runner.send(str(result))
    print("sent result to dispatcher")
    print("received message from dispatcher: {}".format(runner.recv()))
    runner.close()
except Exception as e:
    runner.close()
    print(e)
    sys.exit()