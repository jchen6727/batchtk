from pubtk.runtk.runners import create_runner
from pubtk.netpyne import specs
import sys
# hack workaround to NetPyNE stuff.
class Sim_Wrapper(object): # basically the __init__.py from netpyne/sim ....
    # import loading functions
    def __init__(self):
        from netpyne import sim
        self.sim = sim
    def __getattr__(self, item):
        return getattr(self.sim, item)


class Pubtk_Sim(Sim_Wrapper):

    def __init__(self, runner_type='socket'):
        super().__init__()
        self.runner = specs

    def initialize(self, netParams=None, simConfig=None, net=None):
        #print("initializing network")
        self.sim.initialize(netParams, simConfig, net)
        self.runner.connect()
    def set_runner(self, runner_type='socket'):
        self.runner = create_runner(runner_type)
    def get_rank(self):
        try:
            return self.rank
        except Exception as e:
            print("currently no rank as the sim object has not been initialized: {}".format(e))
            return 0

    def is_host(self):
        return self.get_rank() == 0
    def send(self, data):
        if self.is_host():
            self.runner.send(data)

    def recv(self): # to be implemented. need to broadcast value to all workers
        pass

    def sync(self):
        self.sim.pc.barrier()
    def close(self):
        self.sync()
        self.sim.clearAll()
        self.runner.close()
        sys.exit(0)
