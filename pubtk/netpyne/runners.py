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
        new_class = runners[inherit]
    netParams = object()
    cfg = object()
    def __init__(self, netParams=None, cfg=None, **kwargs):
        super().__init__(grepstr=runtk.GREPSTR,
                         aliases={
                             'socketfile': 'SOCFILE',
                             'jobid': 'JOBID',
                         },
                         **kwargs
                         )
        self.netParams = netParams
        self.cfg = cfg

    def get_netParams(self):
        if self.netParams:
            return self.netParams
        else:
            from netpyne import specs
            self.netParams = specs.NetParams()
            return self.netParams

    def get_cfg(self):
        if self.cfg:
            return self.cfg
        else:
            from netpyne import specs
            self.cfg = specs.SimConfig()
            return self.cfg

    def set_mappings(self, filter=''):
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

