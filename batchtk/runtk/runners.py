import os
import json
from batchtk import runtk
from batchtk.runtk.sockets import INETSocket, UNIXSocket
import socket
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import ast
import warnings

class Runner(object):
    """
    base class for all Runner classes
    Handles parsing and injection of passed variables (env) into the python script's namespace. This serves as a base
    class for all runners.

    contains placeholder (pass) functions inherited by child functions to allow for verbatim calls that are agnostic to
    the specific inherited class.
    """

    _instance = None #singleton instance
    _initialized = False
    _reinstance = False
    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation
        Parameters
        ----------
        args - see __init__
        kwargs - see __init__

        Examples
        --------
        runner = get_runner()
        runner_id = id(runner)
        with get_runner() as comm:
            id(comm) == runner_id
        """
        if cls._instance is None or cls._reinstance is not False:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(
        self,
        grepstr: Optional[str] = None, #expecting string, defaults to runtk.GREPSTR (header.py)
        env: Optional[Dict] = None, #expecting dictionary, this UPDATES the dictionary of already passed variables (env)
        aliases: Optional[Dict] = None, #expecting dictionary, defaults to empty dictionary
        supports: Optional[Dict] = None, #expecting dictionary, defaults to runtk.SUPPORTS (header.py)
        log: Optional[Union[str, logging.Logger]] = None, #expecting string or logging.Logger instance, the string will create a log.
        **kwargs
    ):
        """
        initializes base runner class
        *Optional* Parameters
        ----------
        grepstr  - a string identifier to select relevant environment variables, defaults to runtk.GREPSTR
        env      - a dictionary including any additional environmental variables to be used by the created runner
        aliases  - a dictionary of attribute aliases: e.g. {'alias': 'attribute'}
        supports - a dictionary of supported types and deserialization functions,
                   the Runner supports 'FLOAT', 'JSON', 'STRING' by default, (see runtk.SUPPORTS)
                   the user supplied argument can supplant these deserialization
                   functions
        log      - a string or logging.Logger instance that creates a log for runtime, if not provided, no logging
                   will be done. If a string is provided, a log file will be created with the string as the name.
        **kwargs - unused placeholder
        """
        # Initialize logger
        if self._initialized and not self._reinstance:
            if grepstr or aliases or supports or log or env:
                warnings.warn("Runner has already been initialized, ignoring grepstr, aliases, supports, log, env args.")
            return
        self._initialized = not self._reinstance
        self.logger = log
        if isinstance(log, str):
            self.logger = logging.getLogger(log)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler("{}.log".format(log))
            formatter = logging.Formatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        if isinstance(log, logging.Logger):
            pass
        self.env = os.environ.copy()
        env and self.env.update(env) # update the self.env if (env) evaluates to True
        self.aliases = aliases or {}
        self.supports = supports or runtk.SUPPORTS
        self.grepstr = grepstr or runtk.GREPSTR
        self.grepfunc = staticmethod(lambda key: self.grepstr in key )
        self.greptups = {key: self.env[key].split(runtk.EQDELIM) for key in self.env if
                         self.grepfunc(key)}
        # readability, greptups as the environment variables: (key,value) passed by runtk.GREPSTR environment variables
        # saved the environment variables TODO JSON vs. STRING vs. FLOAT
        self.mappings = self.load_env()
        if kwargs:
            self.log("Unused arguments were passed into base class Runner.__init__(): {}".format(kwargs), level='info')

    def get_mappings(self):
        """
        Returns
        -------
        self.mappings, a dictionary of deserialized environment variables
        """
        return self.mappings

    def __getattr__(self, k): # if __getattribute__ fails, check for k in env, aliases
        if k in self.env:#
            return self.env[k]
        elif k in self.aliases:
            return self.env[self.aliases[k]]
        #elif k in [...]: #TODO not going to worry about __getattr__ this for now..., should return from __getattribute__
        #    return object.__getattribute__(self, k)
        else:
            raise AttributeError(k) # consistency with hasattr-- this way it will return False instead of an exception

    def __getitem__(self, k):
        try:
            return object.__getattribute__(self, k)
        except:
            raise KeyError(k)

    def load_env(self): #clarity, loads an entire environment, load_var loads a single variable from the environment
        mappings = {
            # export JSONPMAP0="cfg.settings={...}" for instance would map the {...} as a json to cfg.settings
            val[0].strip(): self.load_var(key.split(self.grepstr)[0], val[1].strip())
            for key, val in self.greptups.items()
        }
        return mappings
    def load_var(self, _type: str, val: object):#NOTE, rename convert to
        """
        Internal function called during initialization for converting environment values to the appropriate type
        (see runtk.SUPPORTS)
        Returns
        -------
        self.supports[_type](val)
        """
        if _type in self.supports:
            return self.supports[_type](val)
        try:
            return ast.literal_eval(val)
        except:
            raise ValueError(val)

    def connect(self, **kwargs):
        """
        Method for connecting to the host (dispatcher) if bidirectional communication is implemented
        (see runtk.SocketRunner)
        If it is implemented, it will be a blocking call.
        Otherwise returns None (can be called but will do nothing)
        """
        return None

    def write(self, data, **kwargs):
        """
        Method for writing data for the host (dispatcher) to read, will redirect to send for socket based communication
        (see SocketRunner, FileRunner)
        Parameters
        ----------
        data - the data to be sent to the Dispatcher (to be caught in the dispatchers .recv() method
        """
        pass
    def signal(self, **kwargs):
        """
        Method for signaling to the host (dispatcher) necessary for file based communication
        (see FileRunner)
        """
        pass

    def log(self, message, level='info'):
        """
        Method for logging messages
        Parameters
        ----------
        message - the string to be logged
        level   - *Optional* the level of the log message, defaults to 'info'
        """
        if self.logger:
            getattr(self.logger, level)(message)
    def send(self, data, **kwargs):
        """
        Method for sending data to the host (dispatcher). To be implemented by inherited classes.
        Parameters
        ----------
        data - the data to be sent to the Dispatcher (to be caught in the dispatcher's .recv() method)
        """
        pass

    def recv(self, **kwargs):
        """
        Method for receiving data from the host (dispatcher). To be implemented by inherited classes.
        Method is a blocking call if implemented, it will wait until the data is received.
        Returns
        -------
        data - the data sent from the dispatcher (data = runner.recv() <- dispatcher.send(data))
        """
        return None
    def close(self, **kwargs):
        """
        Method called at close of the script, cleans up any open file handles or sockets, etc. To be implemented by
        inherited classes. Also resets the script to allow for reinitialization of a new Runner
        """
        self._instance = None
        self._initialized = False
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # note
        # exc_type, exc_val, exc_tb are the exception type, value, and traceback
        #if exc_type:
        #    print("Exception: {}".format(exc_tb))
        #    print("closing connection")
        self.close()
        #print("connection closed")



class FileRunner(Runner):
    """
    Extension of base Runner class that handles communication with the dispatcher by reading and writing to the file
    system. As long as the Dispatcher and FileRunner share the same file system, this method allows communication of
    arbitrary data one way from the FileRunner to the Dispatcher
    see class runner
    * only supports one way communication during runtime, FileRunner.send() -> Dispatcher.recv()
    (from runner back to dispatcher through .write, .signal .send methods)

    custom aliases -> {'signalfile': 'SGLFILE', 'writefile': 'OUTFILE', 'jobid': 'JOBID'}
    can be used to reference environment variables:
    i.e.
    export SGLFILE="foo.sgl" -> runner.signalfile = "foo.sgl"
    export OUTFILE="bar.out" -> runner.writefile = "bar.out"
    export JOBID="1234"      -> runner.jobid = "1234"
    """
    def __init__(self, **kwargs):
        'aliases' in kwargs or kwargs.update(
            {'aliases':
                 runtk.FILE_ALIASES
            }
        )
        super().__init__(**kwargs)

    def signal(self):
        open(self.signal_file, 'w').close()

    def write(self, data, mode = 'w'):
        with open(self.write_file, mode) as fptr:
            fptr.write(data)

    def send(self, data, mode = 'w'):
        self.write(data, mode)
        self.signal()

class SocketRunner(Runner):
    """
    Extension of base Runner class that handles communication with the dispatcher by sending and receiving data through
    a custom socket protocol (implemented in .sockets.py). This method allows for bidirectional communication through
    blocking calls to .connect(), .send(), and .recv() methods. It supports AF_INET and AF_UNIX socket communications.
    see class runner
    * supports bidirectional communication during runtime,
    dispatcher.accept() <-> runner.connect()
    then:
    runner.send(data) -> dispatcher.recv()
    runner.recv()     <- dispatcher.send(data)

    custom aliases -> {'socketname': 'SOCNAME', 'socket_name': 'SOCNAME', 'jobid': 'JOBID'}
    can be used to reference environment variables:
    i.e.
    export SOCNAME="foo.soc" -> runner.socket_name = "foo.soc"
    ...
    """
    def __init__(self, **kwargs):
        'aliases' in kwargs or kwargs.update(
            {'aliases':
                runtk.SOCKET_ALIASES
            }
        )
        super().__init__(**kwargs)
        self.host_socket = None
        self.socket = None

    def connect(self, socket_type=None, timeout=None): #AF_INET == 2
        #timeout = None (blocking), 0 (non-blocking), >0 (timeout in seconds)
        socket_type = not socket_type and os.path.exists(self.socket_name) and socket.AF_UNIX or socket.AF_INET
        match socket_type:
            case socket.AF_INET:
                ip, port = self.socket_name.split(',')
                self.host_socket = (ip.strip(' (\''), int(port.strip(')')))
                self.socket = INETSocket(socket_name=self.host_socket)
            case socket.AF_UNIX:
                self.host_socket = self.socket_name # just a filename
                self.socket = UNIXSocket(socket_name=self.host_socket)
            case _:
                raise ValueError(socket_type)
        self.socket.socket.settimeout(timeout)
        self.socket.connect()
        return self.host_socket

    def write(self, data):
        self.send(data)

    def send(self, data):
        self.socket.send(data)

    def recv(self):
        return self.socket.recv()

    def close(self):
        super().close()
        self.socket.close()

RUNNERS = {
    'socket': SocketRunner,
    'file': FileRunner,
}

def get_class(runner_type = None):
    """
    Factory function for retrieving a runner class. if no runner_type is provided, it will check the environment to
    determine the appropriate runner class.
    Parameters
    ----------
    runner_type - a string specifying the type of runner to be created, must be a key in runners
    Returns
    -------
    runners[runner_type] - a runner instance
    """
    if runner_type is None:
        if runtk.SOCKET_ENV in os.environ:
            return SocketRunner
        if runtk.MSGOUT_ENV in os.environ:
            return FileRunner
        return Runner
    if runner_type in RUNNERS:
        return RUNNERS[runner_type]
    else:
        raise ValueError(runner_type)

def get_runner(runner_type = None, **kwargs):
    """
    Factory function for retrieving a runner class. if no runner_type is provided, it will check the environment to
    determine the appropriate runner class.
    Parameters
    ----------
    runner_type - a string specifying the type of runner to be created, must be a key in runners
    Returns
    -------
    runners[runner_type](**kwargs) - a runner instance
    """
    return get_class(runner_type)(**kwargs)

def get_comm(runner_type = None, **kwargs):
    """
    equivalent to get_runner
    Parameters
    ----------
    runner_type - a string specifying the type of runner to be created, must be a key in runners
    Returns
    -------
    runners[runner_type](**kwargs) - a runner instance
    """
    return get_class(runner_type)(**kwargs)