from pubtk.netpyne import specs
from pubtk.runtk.runners import create_runner
from neuron import h


class Comm(object):
    def __init__(self, runner_type='socket'):
        self.runner = specs
        h.nrnmpi_init()
        self.pc = h.ParallelContext()
        self.rank = self.pc.id()

    def __getattr__(self, item):
        return getattr(self.sim, item)
    def initialize(self):
        if self.is_host():
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
        self.runner.sync()
    def close(self):
        self.sync()
        self.runner.close()
        sys.exit(0)