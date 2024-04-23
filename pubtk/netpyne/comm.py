from pubtk.netpyne import specs
from pubtk.runtk.runners import create_runner
from neuron import h

HOST = 0

class Comm(object):
    def __init__(self, runner = specs):
        self.runner = runner
        h.nrnmpi_init()
        self.pc = h.ParallelContext()
        self.rank = self.pc.id()

    def initialize(self):
        if self.is_host():
            self.runner.connect()


    def set_runner(self, runner_type='socket'):
        self.runner = create_runner(runner_type)
    def is_host(self):
        return self.rank == HOST
    def send(self, data):
        if self.is_host():
            self.runner.send(data)

    def recv(self): # to be implemented. need to broadcast value to all workers
        data = self.is_host() and self.runner.recv()
        self.pc.barrier()
        return self.pc.py_broadcast(data, HOST)

    def close(self):
        self.runner.close()
