import os
import json
from pubtk.runtk.utils import convert, set_map, create_script
from pubtk import runtk
from pubtk.runtk.runners import Runner, SocketRunner, FileRunner
import socket
import logging
import time
runners = {
    'socket': SocketRunner,
    'inet': SocketRunner,
    'unix': SocketRunner,
    'file': FileRunner,
    's': SocketRunner,
    'f': FileRunner,
}

class NetpyneRunner(Runner):
    """
    runner for netpyne
    see class runner
    mappings <-
    """
    def __new__(cls, inherit='s', **kwargs):
        if inherit in runners:
            _super = runners[inherit]
        else:
            _super = SocketRunner

        def __init__(self, netParams=None, cfg=None, **kwargs):
            _super.__init__(self, **kwargs)
            self.netParams = netParams
            self.cfg = cfg

        def _set_inheritance(self, inherit):
            if inherit in runners:
                cls = type(self)
                cls.__bases__ = (runners[inherit],)

        def get_NetParams(self): #change nomenclature to match NetPyNE
            if self.netParams:
                return self.netParams
            else:
                from netpyne import specs
                self.netParams = specs.NetParams()
                return self.netParams

        def update_cfg(self): #intended to take `cfg` instance as self
            for assign_path, value in self.__mappings__.items():
                try:
                    set_map(self, assign_path, value)
                except Exception as e:
                    raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))

        def get_SimConfig(self):
            if self.cfg:
                return self.cfg
            else:
                from netpyne import specs
                self.cfg = type("Runner_SimConfig", (specs.SimConfig,),
                    {'__mappings__': self.mappings,
                     'update_cfg': update_cfg})()
                return self.cfg

        def set_SimConfig(self):
            # assumes values are only in 'cfg'
            for assign_path, value in self.mappings.items():
                try:
                    set_map(self, "cfg.{}".format(assign_path), value)
                except Exception as e:
                    raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))

        def set_mappings(self, filter=''):
            # arbitrary filter, can work with 'cfg' or 'netParams'
            for assign_path, value in self.mappings.items():
                if filter in assign_path:
                    set_map(self, assign_path, value)

        return type("NetpyneRunner{}".format(str(_super.__name__)), (_super,),
                    {'__init__': __init__,
                     '_set_inheritance': _set_inheritance,
                     'get_NetParams': get_NetParams,
                     'NetParams': get_NetParams,
                     'SimConfig': get_SimConfig,
                     'get_SimConfig': get_SimConfig,
                     'set_SimConfig': set_SimConfig,
                     'set_mappings': set_mappings})(**kwargs) # need to override __init__ or else will call parent
