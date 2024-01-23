import os
import json
from pubtk.runtk.utils import convert, set_map, create_script
from pubtk import runtk
import socket
import time

class Runner(object):
    """
    Handles parsing and injection of environmental variables into python script.
    """
    def __init__(
        self,
        grepstr=runtk.GREPSTR,
        env = False,
        aliases = False,
        supports = False,
        **kwargs
    ):
        """
        Parameters
        ----------
        grepstr - the string identifier to select relevant environment variables
        env - any additional variables to be used by the created runner
        aliases - dictionary of attribute aliases: e.g. {'alias': 'attribute'}
        supports - dictionary of supported types and deserialization functions,
                   the Runner supports 'FLOAT', 'JSON', 'STRING' by default,
                   the user supplied argument can supplant these deserialization
                   functions
        **kwargs - unused placeholder
        """
        self.env = os.environ.copy()
        env and self.env.update(env) # update the self.env if (env) evaluates to True
        self.aliases = {}
        aliases and self.aliases.update(aliases)
        self.supports = {
                         'INT': int,
                         'FLOAT': float,
                         'JSON': json.loads,
                         'DICT': json.loads,
                         'STR': staticmethod(lambda val: val),
                         }
        supports and self.supports.update(supports)

        #self.debug.append("grepstr = {}".format(grepstr))
        self.grepstr = grepstr
        self.grepfunc = staticmethod(lambda key: grepstr in key )
        self.greptups = {key: self.env[key].split('=') for key in self.env if
                         self.grepfunc(key)}
        #self.debug = [self.greptups, self.env]
        #print(self.debug)
        # readability, greptups as the environment variables: (key,value) passed by runtk.GREPSTR environment variables
        # saved the environment variables TODO JSON vs. STRING vs. FLOAT
        self.mappings = {
            val[0].strip(): self.convert(key.split(grepstr)[0], val[1].strip())
            for key, val in self.greptups.items()
        }
        # export JSONPMAP0="cfg.settings={...}" for instance would map the {...} as a json to cfg.settings

    def get_debug(self):
        return self.debug

    def get_mappings(self):
        return self.mappings

    def __getattr__(self, k):
        if k in self.env:
            return self.env[k]
        elif k in self.aliases:
            return self.env[self.aliases[k]]
        else:
            raise KeyError(k)

    def __getitem__(self, k):
        try:
            return object.__getattribute__(self, k)
        except:
            raise KeyError(k)

    def convert(self, _type: str, val: object):
        if _type in self.supports:
            return self.supports[_type](val)
        if _type == '':
            for _type in self.supports:
                try:
                    return self.supports[_type](val)
                except:
                    pass
        raise KeyError(_type)

class HPCRunner(Runner):
    def __init__(self, **kwargs):
        aliases = {'signalfile': 'SGLFILE',
                   'writefile': 'OUTFILE',
                   'socketfile': 'SOCFILE', #all SOC deprecated for SOCNAME
                   'socketip': 'SOCIP', #all SOC deprecated for SOCNAME
                   'socketport': 'SOCPORT', #all SOC deprecated for SOCNAME
                   'jobid': 'JOBID',
                   'socketname': 'SOCNAME',
                   }
        if 'aliases' in kwargs:
            kwargs['aliases'].update(aliases)
        else:
            kwargs['aliases'] = aliases
        super().__init__(**kwargs)
        self.host_socket = None
        self.socket = None

    def connect(self, socket_type=socket.AF_INET, timeout=1): #AF_INET == 2
        #timeout = None (blocking), 0 (non-blocking), >0 (timeout in seconds)
        match socket_type:
            case socket.AF_INET:
                ip, port = self.socketname.split(',')
                self.host_socket = (ip.strip(' (\''), int(port.strip(')')))
            case socket.AF_UNIX:
                self.host_socket = self.socketname # just a filename
            case _:
                raise ValueError(socket_type)
        self.socket = socket.socket(socket_type, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect(self.host_socket)
        return self.host_socket

    def write(self, data):
        fptr = open(self.writefile, 'w')
        fptr.write(data)
        fptr.close()

    def signal(self):
        open(self.signalfile, 'w').close()

    def send(self, data):
        """
        # send data to socket
        # data: data to send
        # size: size of data to send
        """
        self.socket.sendall(data.encode())

    def recv(self, size=1024):
        """
        # receive data from socket
        # size: size of data to receive
        """
        return self.socket.recv(size).decode()

    def close(self):
        """
        # close socket connection
        """
        self.socket.close()

class NetpyneRunner(HPCRunner):
    """
    # runner for netpyne
    # see class runner
    mappings <-
    """
    netParams = object()
    cfg = object()
    def __init__(self, netParams=None, cfg=None, **kwargs):
        super().__init__(grepstr=runtk.GREPSTR,
                         aliases={
                             'signalfile': 'SGLFILE',
                             'writefile': 'OUTFILE',
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
