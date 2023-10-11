import os
import json
from .utils import convert, set_map, create_script
from .template import sge_template
import socket
import time

class Runner(object):
    """
    Handles parsing and injection of environmental variables into python script.
    """
    def __init__(
        self,
        grepstr='PUBTK',
        env = None,
        aliases = None,
        supports = None,
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
        if env:
            self.env.update(env)
        self.aliases = {}
        if aliases:
            self.aliases.update(aliases)
        self.supports = {'FLOAT': float,
                         'JSON': json.loads,
                         'STRING': staticmethod(lambda val: val),
                         }
        if supports:
            self.supports.update(supports)
        #self.debug.append("grepstr = {}".format(grepstr))
        self.grepstr = grepstr
        self.grepfunc = staticmethod(lambda key: grepstr in key )
        self.greptups = {key: self.env[key].split('=') for key in self.env if
                         self.grepfunc(key)}
        self.debug = [self.env]
        # readability, greptups as the environment variables: (key,value) passed by 'PMAP' environment variables
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
                   'socketfile': 'SOCFILE',
                   'jobid': 'JOBID'
                   }
        if 'aliases' in kwargs:
            kwargs['aliases'].update(aliases)
        else:
            kwargs['aliases'] = aliases
        super().__init__(**kwargs)

    def connect(self):
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        while True:
            try:
                self.client.connect(self.socketfile)
                break
            except:
                pass

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
        self.client.sendall(data.encode())

    def recv(self, size=1024):
        """
        # receive data from socket
        # size: size of data to receive
        """
        return self.client.recv(size).decode()

    def close(self):
        """
        # close socket connection
        """
        self.client.close()

class NetpyneRunner(HPCRunner):
    """
    # runner for netpyne
    # see class runner
    mappings <-
    """
    netParams = object()
    cfg = object()
    def __init__(self, netParams=None, cfg=None):
        super().__init__(grepstr='PUBTK',
                         aliases={
                             'signalfile': 'SGLFILE',
                             'writefile': 'OUTFILE',
                             'socketfile': 'SOCFILE',
                             'jobid': 'JOBID',
                         }
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
