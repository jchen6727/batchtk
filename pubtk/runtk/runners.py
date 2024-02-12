import os
import json
from pubtk.runtk.utils import convert, set_map, create_script
from pubtk import runtk
import socket
import logging
import time

class Runner(object):
    """
    Handles parsing and injection of environmental variables into python script.
    """
    def __init__(
        self,
        grepstr = None, #expecting string
        env = None, #expecting dictionary
        aliases = None, #expecting dictionary
        supports = None, #expecting dictionary
        log = None, #expecting string
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
        # Initialize logger
        self.logger = log
        if self.logger:
            self.logger = logging.getLogger(log)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler("{}.log".format(log))
            formatter = logging.Formatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.env = os.environ.copy()
        env and self.env.update(env) # update the self.env if (env) evaluates to True
        self.aliases = aliases or runtk.ALIASES
        self.supports = supports or runtk.SUPPORTS

        #self.debug.append("grepstr = {}".format(grepstr))
        self.grepstr = grepstr or runtk.GREPSTR
        self.grepfunc = staticmethod(lambda key: self.grepstr in key )
        self.greptups = {key: self.env[key].split('=') for key in self.env if
                         self.grepfunc(key)}
        # readability, greptups as the environment variables: (key,value) passed by runtk.GREPSTR environment variables
        # saved the environment variables TODO JSON vs. STRING vs. FLOAT
        self.mappings = { # export JSONPMAP0="cfg.settings={...}" for instance would map the {...} as a json to cfg.settings
            val[0].strip(): self.convert(key.split(grepstr)[0], val[1].strip())
            for key, val in self.greptups.items()
        }
        if kwargs:
            self.log("Unused arguments were passed into Runner.__init__(): {}".format(kwargs), level='info')

    def get_debug(self):
        return self.debug

    def get_mappings(self):
        return self.mappings

    def __getattr__(self, k): # if __getattribute__ fails, check for k in env, aliases
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

    def connect(self, **kwargs):
        return None
    def write(self, **kwargs):
        pass
    def signal(self, **kwargs):
        pass

    def log(self, message, level='info'):
        if self.logger:
            getattr(self.logger, level)(message)
    def send(self, **kwargs):
        pass
    def recv(self, **kwargs):
        return None
    def close(self, **kwargs):
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()


class FileRunner(Runner):
    """
    # runner for file based runners
    # see class runner
    # only supports one way communication
    # (from runner back to dispatcher)
    """
    def __init__(self, **kwargs):
        'aliases' in kwargs or kwargs.update(
            {'aliases':
                 {'signalfile': 'SGLFILE',
                  'writefile': 'OUTFILE',
                  'jobid': 'JOBID'}
            }
        )
        super().__init__(**kwargs)

    def signal(self):
        open(self.signalfile, 'w').close()

    def write(self, data, mode = 'w'):
        with open(self.writefile, mode) as fptr:
            fptr.write(data)

    def send(self, data, mode = 'w'):
        self.write(data)
        self.signal()

class SocketRunner(Runner): # socket based runner
    def __init__(self, **kwargs):
        'aliases' in kwargs or kwargs.update(
            {'aliases':
                {'socketname': 'SOCNAME',
                 'jobid': 'JOBID'}
            }
        )
        super().__init__(**kwargs)
        self.host_socket = None
        self.socket = None

    def connect(self, socket_type=socket.AF_INET, timeout=None): #AF_INET == 2
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
        super().close()
        """
        # close socket connection
        """
        self.socket.close()

