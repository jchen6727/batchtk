"""
All Dispatcher classes are defined here:
Dispatcher classes handle the submission and monitoring of jobs





"""

from abc import ABC, abstractmethod
import os
from collections import namedtuple
import time
import subprocess
from batchtk import runtk
from batchtk.runtk.submits import Submit
from batchtk.runtk.sockets import INETSocket, UNIXSocket
from batchtk.utils import create_path, format_env, BaseFS, CustomFS, BaseCmd, CustomCmd, FS_Protocol, Cmd_Protocol

import socket

class Dispatcher(object):
    """
    base class for all Dispatcher classes
    Handles parsing and injection of passed variables (env) to Runner script, submitting the script to a Runner
    and retrieving outputs

    initialized values:
    env ->
        dictionary of values to be exported to the simulation environment, can be within the subprocess call,
        or an environment script (some shell, env equivalent)
    grepstr ->
        the string value used in label generation (specifically the environment dictionary)
        defaults to runtk.GREPSTR ('RUNTK') (see ./header.py)
    label ->
        an ID string that is unique to a Dispatcher <-> Runner pair. If it is not provided, it will be generated
        upon subprocess call by the environment dictionary and **kwargs
    """ 
    #obj_count = 0 # persistent count N.B. may be shared between objects. TODO no utility for this

    def __init__(self, label=None, env=None, grepstr=runtk.GREPSTR, **kwargs):
        """
        initializes base dispatcher class
        *Optional* Parameters
        ----------
        env     - any environmental variables to be passed to the created runner -> note that they will not undergo the formatting for parse by the opposite runner
        grepstr - the string ID for a subprocess to identify environment variables passed by the dispatcher
        label   - an ID string that is unique to the dispatcher <-> runner pair
        **kwargs are placed into a __dict__ item that can be accessed by __getattr__

        initializes label, will set if the argument is supplied, otherwise the value will be
        created upon subprocess call.
        """

        #self.__dict__ = kwargs # the __dict__ has to come first or else env won't work...?
        #TODO what is the purpose of implementing a self.__dict__ in the FIRST place?
        if label is None:
            raise ValueError("label must be provided")
        self.label = label
        self.env = env or {} # if env is None, then set to empty dictionary
        self.grepstr = grepstr

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean() # clean any files that are no longer necessary
        self.close() # close any connections

    def update_env(self, dictionary, value_type=None, format = True, **kwargs):
        """
        Function used to update the environment dictionary that will be passed to the Runner object

        Parameters
        ----------
        dictionary - the dictionary of key: values to add to self.env
        value_type (optional) - defaults to None, the type of the values added in the dictionary, will "cast" all values
        to value_type, otherwise will infer the type of the value by the dictionary entries. Relevant if format is True
        (see format_env())
        format (optional) - defaults to True, if True, the dictionary will be formatted by format_env() before being
        added to self.env, otherwise the dictionary will be added verbatim.

        Returns
        -------
        None

        the entries are added to the environment, either formatted (if format = True) or unformatted (if format = False):

        use:
        .update_env({'foo': 1, 'bar': 2.0, 'baz': 'three'})
        returns:
        {'INTRUNTK0': 'foo=1', 'FLOATRUNTK1': 'bar=2.0', 'STRRUNTK2': 'baz=three'}

        """
        if format:
            self.env.update(self.format_env(dictionary, value_type=value_type, index=len(self.env)))
        else:
            self.env.update(dictionary)

    def format_env(self, dictionary, value_type=None, index=0):
        """
        Parameters
        ----------
        dictionary - the dictionary of variable_path: values to add to the environment
        index (optional) - the index to start at for environment generation, defaults to 0
        value_type (optional) - forces the type of values added to the dictionary, how the runner interprets the values
                              - if not provided, the value_type will be based on the dictionary item's type per entry basis.
        Returns
        -------
        dictionary of formatted environment variables

        use:
            format_env({'foo': 1, 'bar': 2.0, 'baz': 'three'})
        returns:
            {'INTRUNTK0': 'foo=1', 'FLOATRUNTK1': 'bar=2.0', 'STRRUNTK2': 'baz=three'}

        with runtk.GREPSTR being defined in as 'RUNTK' (see ./header.py)
        """
        return format_env(dictionary=dictionary, value_type=value_type, index=index, grepstr=self.grepstr, eqdelim=runtk.EQDELIM)
        #get_type = staticmethod(lambda x: type(x).__name__)
        #return {"{}{}{}".format(value_type or get_type(value).upper(), self.grepstr, index + i):
        #              "{}{}{}".format(key, runtk.EQDELIM, value) for i, (key, value) in enumerate(dictionary.items())}
        # convert dictionary to proper elements


    create_env = format_env # alias (same function)

    def start(self):
        """
        starts the Runner process (job)
        """

    def connect(self):
        """
        connects to the started Runner process (job)
        """
        pass

    def recv(self):
        """
        receives data from the Runner process
        """

    def save_env(self, filename):
        """
        Parameters
        ----------
        filename - filename to save json to

        saves the environment dictionary to a json file
        """
        import json
        with open(filename, 'w') as fptr:
            json.dump(self.env, fptr)
            fptr.close()

    def __repr__(self):
        return """
label:
{}

env:
{}""".format(self.label, self.env)

    def close(self):
        """
        closes the dispatcher
        """
        pass

    def clean(self, handles=None, **kwargs):
        """
        Method called at close of the script, cleans up any open file handles or sockets, etc. To be implemented by
        inherited classes.
        :param handles: see runtk.HANDLES, passing a list of handles will remove those associated files
        :param kwargs:
        :return:
        """
        pass

def _get_obj_args(self, __class__, **kwargs):
    kwargs.update(kwargs.pop('kwargs'))
    return kwargs

class SHDispatcher(Dispatcher):
    """
    Extension of base Dispatcher that extends functionality to handle shell script submissions, fs, and cmd objects
    """
    def __init__(self, submit=None, project_path=None, output_path=".", fs = None, cmd = None, instance_kwargs = None, **kwargs):
        """
        initializes dispatcher
        project_path - current directory where the relevant files to run are located.
        output_path  - path to output directory, can be either relative if starting with '.' or absolute if starting
                       with '/'. defaults to current directory
        submit       - Submit object (see batchtk.runk.submit)
        in **kwargs:
            label      - string to identify dispatcher by the created runner
            env      - dictionary of environmental variables to be passed to the created runner
        """
        kwargs = _get_obj_args(**locals())
        super().__init__(**kwargs)
        # check all instances are set properly
        if not hasattr(self, 'instance_kwargs') and not hasattr(self, 'fs') and not hasattr(self, 'cmd'):
            self.cmd, self.fs = None, None
            self.instance_kwargs = instance_kwargs or {} # set the kwargs to initialize any instances
            self.instance_kwargs.update({'fs': fs, 'cmd': cmd}) # provide the filesystem and command instances
            self.set_instances(**self.instance_kwargs) # set the instance attributes
        self.project_path = project_path
        self.output_path = create_path(project_path, output_path, self.fs)
        self.submit = submit
        self.handles = None
        self.job_id = -1
        # create a "self.target" that contains the output_path and label?
        #self.label = self.label

    def set_instances(self, fs, cmd, **kwargs):
        """
        creates/assigns any instances to the class
        """
        if not hasattr(self, 'instance_kwargs'):
            kwargs = _get_obj_args(**locals())
            self.instance_kwargs = kwargs
        self.fs = CustomFS(fs) #passthrough if valid BaseFS
        self.cmd = CustomCmd(cmd) #passthrough if valid BaseCmd

    def unset_instances(self):
        """
        unsets instances
        """
        self.fs.close()
        self.cmd.close()
        self.fs, self.cmd = None, None

    def reset_instances(self):
        """
        resets instances
        """
        self.unset_instances()
        self.set_instances(**self.instance_kwargs)

    def create_job(self, **kwargs):
        """
        creates a job through the submit instance
        the `label` is created, and the relevant commands and scripts are created,
        then the handles are retrieved from the submit instance

        :param kwargs: #TODO use this format in all docstrings :/
        :return:
        """
        self.submit.create_job(label=self.label,
                               project_path=self.project_path,
                               output_path=self.output_path,
                               env=self.env,
                               **kwargs)
        self.handles = self.submit.get_handles()

    def submit_job(self):
        """
        submits the job through the submit instance
        """
        self.job_id = self.submit.submit_job(fs=self.fs, cmd=self.cmd)


    def start(self, **kwargs):
        """
        creates and submits a job through the submit instance
        (calls .create_job() and .submit_job())
        :param kwargs:
        :return:
        """
        self.create_job(**kwargs)
        self.job_id = self.submit.submit_job(fs=self.fs, cmd=self.cmd)

    def connect(self, **kwargs):
        """
        Method for accepting a connection from a peer (runner) if bidirectional communication is implemented
        (see runtk.UNIX_Dispatcher, runtk.INET_Dispatcher, runtk.SocketRunner)
        If it is implemented, it will be a blocking call.
        Otherwise will simply pass
        :param kwargs:
        :return:
        """
        pass

    def recv(self, **kwargs):
        """
        Method for receiving data from the host (dispatcher). To be implemented by inherited classes.
        Method is a blocking call if implemented, it will wait until the data is received.
        Otherwise, will be a nonblocking function returning None
        Returns
        -------
        data - the data sent from the dispatcher (data = runner.recv() <- dispatcher.send(data))
        """
        return None

    def send(self, data, **kwargs):
        """
        Method for sending data to the host (dispatcher). To be implemented by inherited classes.
        Parameters
        ----------
        data - the data to be sent to the Dispatcher (to be caught in the dispatcher's .recv() method)
        """
        pass

    def close(self):
        """
        closes any relevant dispatcher instances
        """
        self.fs.close()

    def clean(self, handles = None, **kwargs):
        """
        Method called at close of the script, cleans up any open file handles or sockets, etc. To be implemented by
        inherited classes.
        :param handles: see runtk.HANDLES, passing a list of handles will remove those associated files
        :param kwargs:
        :return:
        """
        if handles == 'all':
            handles = list(self.handles.keys())
        if handles:
            for handle in handles:
                if self.fs.exists(self.handles[handle]):
                    self.fs.remove(self.handles[handle])
                #self.handles.pop(handle)

    def __repr__(self):
        repr = super().__repr__()
        repr += """
submit:
------------------------------
{}
""".format(self.submit)


class _Status(namedtuple('status', ['status', 'msg'])):
    def __repr__(self):
        return 'status={}, msg={}'.format(self.status, self.msg)

class QSDispatcher(SHDispatcher):
    """
    Base class for all Query Status Dispatcher classes that utilize a file system instance to query status and cmd instance
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'fs') and not isinstance(self.fs, BaseFS):
            raise ValueError("fs either not created or is not a subclass of BaseFS")
        if not hasattr(self, 'cmd') and not isinstance(self.cmd, BaseCmd):
            raise ValueError("cmd either not created or is not a subclass of BaseCmd")

    def get_handles(self):
        if not self.handles:
            self.create_job()
        return self.handles

    def check_status(self):
        handles = self.get_handles()
        submit, msgout, sglout = handles[runtk.SUBMIT], handles[runtk.MSGOUT], handles[runtk.SGLOUT]
        if not self.fs.exists(submit):
            return _Status(runtk.STATUS.NOTFOUND, None)
        if not self.fs.exists(msgout):
            return _Status(runtk.STATUS.PENDING, None)
        msg = self.fs.tail(msgout)
        if self.fs.exists(sglout):
            return _Status(runtk.STATUS.COMPLETED, msg)
        return _Status(runtk.STATUS.RUNNING, msg)

    def submit_job(self):
        """
        Method for submitting a job that performs a status query first --
        if the job is not found,
        """
        status = self.check_status()
        if status.status in [runtk.STATUS.PENDING, runtk.STATUS.RUNNING, runtk.STATUS.COMPLETED]:
            return status
        if status.status is runtk.STATUS.NOTFOUND:
            proc = self.submit.submit_job(fs=self.fs, cmd=self.cmd)
            self.job_id = proc
            return self.check_status()
        return status

    def check_msg(self):
        status = self.check_status()
        if status.status == runtk.STATUS.COMPLETED:
            return status.msg[0]
        return False

    def start(self, restart=False, **kwargs):
        if restart:
            # manually create job, then ensure call to submit.submit_job
            self.create_job(**kwargs)
            self.job_id = self.submit.submit_job(fs=self.fs, cmd=self.cmd)
        else:
            self.job_id = self.submit_job()

    def recv(self, interval=60, **kwargs):
        data = False
        while not data:
            data = self.check_msg()
            if data:
                return data
            time.sleep(interval)


class SSHDispatcher(QSDispatcher):
    """
    SSH Dispatcher, for running jobs on remote machines
    uses fabric, paramiko
    """
    def __init__(self, connection=None, fs=None, cmd=None, submit=None, remote_dir=None,
                 remote_out='.', env=None, label=None, **kwargs):
        """
        Parameters
        ----------
        host - the ssh host
        cmdstr - the command to run on the remote machine
        env - any environmental variables to be inherited by the created runner
        """
        self.fs = None
        self.connection = None
        self.cmd = None
        self.instance_kwargs = None
        self.set_instances(connection=connection, fs=fs, cmd=cmd)
        super().__init__(submit=submit, project_path=remote_dir, output_path=remote_out, label=label, env=env,
                         fs=self.fs, cmd=self.cmd, instance_kwargs=self.instance_kwargs, connection=self.connection, **kwargs)

    def set_instances(self, connection, fs=None, cmd=None, **kwargs):
        from batchtk.utils import RemoteConnFS, RemoteConnCmd
        self.connection = connection
        self.fs = fs or RemoteConnFS(self.connection)
        self.cmd = cmd or RemoteConnCmd(self.connection)
        super().set_instances(fs=self.fs, cmd=self.cmd, connection=self.connection)

    def unset_instances(self):
        super().unset_instances()
        self.connection.close()
        self.connection = None # keep self.connection

def _set_local_instances(self, fs=None, cmd=None, **kwargs):
    from batchtk.utils import LocalProcCmd, LocalFS
    self.fs = fs or LocalFS()
    self.cmd = cmd or LocalProcCmd()
    SHDispatcher.set_instances(self, fs=self.fs, cmd=self.cmd)

class LocalDispatcher(QSDispatcher):
    """
    SH Dispatcher, for running jobs on local machines (LocalProcCmd and LocalFS)
    """
    def __init__(self, fs=None, cmd=None, submit=None, project_path=None,
                 output_path='.', env=None, label=None, **kwargs):
        """
        Parameters
        ----------
        cmdstr - the command to run on the remote machine
        env - any environmental variables to be inherited by the created runner
        """
        self.fs = None
        self.cmd = None
        self.instance_kwargs = None
        self.set_instances(fs=fs, cmd=cmd)
        super().__init__(submit=submit, project_path=project_path, output_path=output_path, label=label, env=env,
                         fs=self.fs, cmd=self.cmd, instance_kwargs=self.instance_kwargs, **kwargs)

    def set_instances(self, fs=None, cmd=None, **kwargs):
        _set_local_instances(self, fs=fs, cmd=cmd, **kwargs)

class SOCKETDispatcher(SHDispatcher):
    """
    Base class for socket-based dispatchers
    """
    def __init__(self, **kwargs):
        self.fs = None
        self.cmd = None
        self.instance_kwargs = None
        self.socket = None
        self.set_instances()
        self.handles = None
        super().__init__(**kwargs)

    def set_instances(self, fs=None, cmd=None, **kwargs):
        _set_local_instances(self, fs=fs, cmd=cmd, **kwargs)

    def start(self, **kwargs):
        self.create_job(**kwargs)
        self.submit_job()

    def connect(self):
        """
        accept incoming connection from client
        this function is blocking
        """
        connection, peer_address = self.socket.accept()  # actual blocking statement
        return connection, peer_address

    def recv(self, interval=0):
        """
        # interval does nothing, used to generalize interfaces...
        Returns
        -------

        """
        return self.socket.recv()

    def send(self, data):
        self.socket.send(data)

    def close(self):
        super().close()
        if self.socket:
            self.socket.close()
        self.socket = None

    def get_handles(self):
        return self.handles

    def clean(self, handles=None):
        self.close()
        super().clean(handles=handles)


class UNIXDispatcher(SOCKETDispatcher):
    """
    AF UNIX Dispatcher utilizing sockets (requires socket forwarding)
    handles submitting the script to a Runner/Worker object

    #TODO can we consolidate UNIXDispatcher and INETDispatcher into a single class?
    """
    def create_job(self, **kwargs):
        socket_name = "{}/{}.s".format(self.output_path, self.label)  # the socket file
        self.socket = UNIXSocket(socket_name = socket_name)
        self.socket.listen()
        self.submit.create_job(label=self.label, project_path=self.project_path,
                               output_path=self.output_path, env=self.env, sockname=socket_name, **kwargs)
        self.handles = self.submit.get_handles()
        #TODO if doing stale socket handling....
        #try:
        #    os.unlink(socket_name)
        #except OSError as e:
        #    if os.path.exists(socket_name):
        #        raise OSError("issue when creating socket {}:".format(socket_name), e)

class INETDispatcher(SOCKETDispatcher):
    """
    AF INET Dispatcher utilizing sockets
    handles submitting the script to a Runner/Worker object
    """
    def create_job(self, **kwargs):
        self.socket = INETSocket()
        socket_name = self.socket.listen() # one server <-> one client
        self.submit.create_job(label=self.label, project_path=self.project_path,
                               output_path=self.output_path, env=self.env, sockname=socket_name, **kwargs)
        self.handles = self.submit.get_handles()

class NOFDispatcher(Dispatcher):
    """
    No File Dispatcher, everything is run without generation of shell scripts.
    ? utility of NOF_Dispatcher vs. UNIX ?
    """
    def __init__(self, cmdstr='', env=None, **kwargs):
        """
        Parameters
        ----------
        initializes dispatcher
        cmdstr - command line call to be executed by the created runner (subprocess.run())
        env - any environmental variables to be inherited by the created runner
        """
        super().__init__(env=env, **kwargs)
        self.cmdstr = cmdstr
        self.env.update(os.environ.copy())

    def run(self):
        self.proc = subprocess.run(self.cmdstr.split(), env=self.env, text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        return self.proc

DISPATCHERS = {
    'INET': INETDispatcher,
    'UNIX': UNIXDispatcher,
    'SFS': LocalDispatcher,
    'NOF': NOFDispatcher,
    'SSH': SSHDispatcher,
}

def create_dispatcher(dispatcher_type):
    """
    Factory function for creating a dispatcher constructor
    Parameters
    ----------
    runner_type - a string specifying the type of dispatcher to be created, must be a key in runners
    Returns
    -------
    DISPATCHERS[dispatcher_type] - a dispatcher constructor
    """

    if dispatcher_type in DISPATCHERS:
        return DISPATCHERS[dispatcher_type]
    else:
        raise ValueError(dispatcher_type)


