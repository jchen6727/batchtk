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
    """
    def __new__(cls, inherit='s', **kwargs):
        print('__new__')
        if inherit in runners:
            instance = runners[inherit]
        else:
            instance = SocketRunner # default to SocketRunner
        cls.__bases__ = (instance,)
        return super().__new__(cls)
    """
    def __new__(cls, inherit='s', **kwargs):
        print('__new__')
        if inherit in runners:
            _super = runners[inherit]
        else:
            _super = SocketRunner

        def __init__(self, netParams=None, cfg=None, **kwargs):
            print('__init__')
            _super.__init__(self, **kwargs)
            self.netParams = netParams
            self.cfg = cfg

        def _set_inheritance(self, inherit):
            if inherit in runners:
                cls = type(self)
                cls.__bases__ = (runners[inherit],)

        def get_NetParams(self, set=True): #change nomenclature to match NetPyNE
            if set:
                self.set_SimConfig
            if self.netParams:
                return self.netParams
            else:
                from netpyne import specs
                self.netParams = specs.NetParams()
                return self.netParams

        def get_SimConfig(self):
            if self.cfg:
                return self.cfg
            else:
                from netpyne import specs
                self.cfg = specs.SimConfig()
                return self.cfg

        def set_mappings(self, filter=''):
            # arbitrary filter, can work with 'cfg' or 'netParams'
            for assign_path, value in self.mappings.items():
                if filter in assign_path:
                    set_map(self, assign_path, value)

        return type("NetpyneRunner{}".format(str(_super.__name__)), (_super,),
                    {'__init__': __init__,
                     '_set_inheritance': _set_inheritance,
                     'get_NetParams': get_NetParams,
                     'get_SimConfig': get_SimConfig,
                     'set_mappings': set_mappings})(**kwargs) # need to override __init__ or else will call parent
    """
    def __init__(self, netParams=None, cfg=None, **kwargs):
        print('__init__')
        super().__init__(**kwargs)
        self.netParams = netParams
        self.cfg = cfg
    """

    def _set_inheritance(self, inherit):
        if inherit in runners:
            cls = type(self)
            cls.__bases__ = (runners[inherit],)

    def get_NetParams(self, set=True): #change nomenclature to match NetPyNE
        if set:
            self.set_SimConfig
        if self.netParams:
            return self.netParams
        else:
            from netpyne import specs
            self.netParams = specs.NetParams()
            return self.netParams

    def get_SimConfig(self):
        if self.cfg:
            return self.cfg
        else:
            from netpyne import specs
            self.cfg = specs.SimConfig()
            return self.cfg

    def set_SimConfig(self):
        # assumes values are only in 'cfg'
        for assign_path, value in self.mappings.items():
            set_map(self.cfg, assign_path, value)

    def set_mappings(self, filter=''):
        # arbitrary filter, can work with 'cfg' or 'netParams'
        for assign_path, value in self.mappings.items():
            if filter in assign_path:
                set_map(self, assign_path, value)


# old runner class
# ----------------
# class NetpyneRunner(SocketRunner):
#     """
#     # runner for netpyne
#     # see class runner
#     mappings <-
#     """
#     netParams = object()
#     cfg = object()
#     def __init__(self, netParams=None, cfg=None, **kwargs):
#         super().__init__(grepstr=runtk.GREPSTR,
#                          aliases={
#                              'socketfile': 'SOCFILE',
#                              'jobid': 'JOBID',
#                          },
#                          **kwargs
#                          )
#         self.netParams = netParams
#         self.cfg = cfg
#
#     def get_netParams(self):
#         if self.netParams:
#             return self.netParams
#         else:
#             from netpyne import specs
#             self.netParams = specs.NetParams()
#             return self.netParams
#
#     def get_cfg(self):
#         if self.cfg:
#             return self.cfg
#         else:
#             from netpyne import specs
#             self.cfg = specs.SimConfig()
#             return self.cfg
#
#     def set_mappings(self, filter=''):
#         for assign_path, value in self.mappings.items():
#             if filter in assign_path:
#                 set_map(self, assign_path, value)

nr = NetpyneRunner()