import os
import subprocess
import hashlib
from pubtk import runtk
from pubtk.runtk.submit import Submit
import socket


def format_env(dictionary, index=0, value_type=None):
    """
    Parameters
    ----------
    dictionary - the dictionary of variable_path: values to add to the environment
    value_type - the type of the values added in the dictionary

    handles any global tasks prior to running the subprocess
        if self.gid = False, generates alphanumeric for self.gid based on self.env and **kwargs
    """
    cl = len(dictionary)
    get_type = staticmethod(lambda x: type(x).__name__)
    return {"{}{}{}".format(value_type or get_type(value).upper(), runtk.GREPSTR, cl + i):
                  "{}={}".format(key, value) for i, (key, value) in enumerate(dictionary.items())}

    # convert dictionary to proper elements
class Dispatcher(object):
    """
    base class for Dispatcher
    handles submitting the script to a Runner/Worker object and retrieving outputs

    initialized values:
    env ->
        dictionary of values to be exported to the simulation environment, either within the subprocess call,
        or to an environment script
    grepstr ->
        the string value that generates labels for relevant values (filename and environment dictionary)
    gid ->
        a generated ID string that is unique to a Dispatcher <-> Runner pair.
    """ 
    obj_count = 0 # persistent count N.B. may be shared between objects.

    def __init__(self, env=False, grepstr=runtk.GREPSTR, gid = False, **kwargs):
        """
        Parameters
        ----------
        initializes dispatcher
        env - any environmental variables to be inherited by the created runner
        grepstr - the string ID for subprocess to identify necessary environment variables
        **kwargs are placed into a __dict__ item that can be accessed by __getattr__
        id, str_id, int_id are special keyword arguments that can be supplied for FS and port handling.

        initializes gid, will set if the argument is supplied, otherwise the value will be
        created upon subprocess call.
        """

        self.__dict__ = kwargs # the __dict__ has to come first or else env won't work...?
        self.env = env or {} # if env is False, then set to empty dictionary
        self.grepstr = grepstr
        self.gid = gid
        Dispatcher.obj_count = Dispatcher.obj_count + 1

    def add_json(self):
        pass
    def update_env(self, dictionary, value_type=None, format = True, **kwargs):
        """
        Parameters
        ----------
        value_type - the type of the values added in the dictionary
        dictionary - the dictionary of variable_path: values to add to the environment

        adds a dictionary of single type <value_type> {variable_path: values} to the environment dictionary self.env
        with the proper formatting (<value_type><self.grepstr><unique_id>: <variable_path><value>)
        Returns
        -------
        the formatted entries added to the environment:
            {<value_type><self.grepstr><unique_id>: <variable_path><value>}
        """
        if format:
            self.env.update(self.format_env(dictionary, value_type=value_type))
        else:
            self.env.update(dictionary)

    def format_env(self, dictionary, value_type=None):
        """
        Parameters
        ----------
        dictionary - the dictionary of variable_path: values to add to the environment
        value_type - the type of the values added in the dictionary

        handles any global tasks prior to running the subprocess
            if self.gid = False, generates alphanumeric for self.gid based on self.env and **kwargs
        """
        cl = len(self.env)
        get_type = staticmethod(lambda x: type(x).__name__)
        return {"{}{}{}".format(value_type or get_type(value).upper(), self.grepstr, cl + i):
                      "{}={}".format(key, value) for i, (key, value) in enumerate(dictionary.items())}

        # convert dictionary to proper elements

    def init_run(self, **kwargs):
        """
        Parameters
        ----------
        **kwargs - of note, **kwargs here is used if necessary to help generate self.gid

        handles any global tasks prior to running the subprocess
            if self.gid = False, generates alphanumeric for self.gid based on self.env and **kwargs
        """
        if not self.gid:
            gstr = str(self.env) + str(kwargs)
            self.gid = hashlib.md5(gstr.encode()).hexdigest()
        self.label = "{}_{}".format(self.grepstr.lower(), self.gid)
        # convert dictionary to proper elements

    def __getattr__(self, k):
        # only called if __getattribute__ fails
        return self.__dict__[k]

    def save_json(self, filename):
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

class NOF_Dispatcher(Dispatcher):
    """
    No File Dispatcher, everything is run without generation of shell scripts.
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
        super().init_run()
        self.proc = subprocess.run(self.cmdstr.split(), env=self.env, text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        return self.proc.stdout, self.proc.stderr

class SH_Dispatcher(Dispatcher):
    """
    Shell based Dispatcher generating shell script to submit jobs
    """
    def __init__(self, cwd="", submit=False, **kwargs):
        """
        initializes dispatcher
        cwd: current working directory
        env: any environmental variables to be inherited by the created runner
        in **kwargs:
            id: string to identify dispatcher by the created runner
            submit: Submit object (see pubtk.runk.submit)
        """
        super().__init__(**kwargs)
        self.cwd = cwd
        self.submit = submit or Submit()
        self.jobid = -1
        #self.label = self.gid

    def create_job(self, **kwargs):
        super().init_run()
        self.submit.create_job(label=self.label,
                               cwd=self.cwd,
                               env=self.env,
                               **kwargs)

    def submit_job(self):
        self.jobid = self.submit.submit_job()

    def run(self, **kwargs):
        self.create_job(**kwargs)
        self.jobid = self.submit.submit_job()

class SFS_Dispatcher(SH_Dispatcher):
    """
    Shared File System Dispatcher utilizing file operations to submit jobs and collect results
    handles submitting the script to a Runner/Worker object
    """

    def create_job(self, **kwargs):
        super().create_job(**kwargs)
        self.watchfile = "{}/{}.sgl".format(self.cwd, self.label)  # the signal file (only to represent completion of job)
        self.readfile = "{}/{}.out".format(self.cwd, self.label)  # the read file containing the actual results
        self.shellfile = "{}/{}.sh".format(self.cwd, self.label)  # the shellfile that will be submitted
        self.runfile = "{}/{}.run".format(self.cwd, self.label)  # the runfile created by the job

    def run(self, **kwargs):
        super().run(**kwargs)

    def get_run(self):
        # if file exists, return data, otherwise return False
        if os.path.exists(self.watchfile):
            fptr = open(self.readfile, 'r')
            data = fptr.read()
            fptr.close()
            return data # what if data itself is False equivalence
        return False

    def clean(self, args='rswo'):
        if args == 'all':
            args = 'rswo'
        if os.path.exists(self.readfile) and 'r' in args:
            os.remove(self.readfile)
        if os.path.exists(self.shellfile) and 's' in args:
            os.remove(self.shellfile)
        if os.path.exists(self.watchfile) and 'w' in args:
            os.remove(self.watchfile)
        if os.path.exists(self.runfile) and 'o' in args:
            os.remove(self.runfile)


class UNIX_Dispatcher(SH_Dispatcher):
    """
    AF UNIX Dispatcher utilizing sockets (requires socket forwarding)
    handles submitting the script to a Runner/Worker object
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.socket = False

    def create_job(self, **kwargs):
        super().create_job()
        self.socketfile = "{}/{}.s".format(self.cwd, self.label)  # the socket file
        try:
            os.unlink(self.socketfile)
        except OSError:
            if os.path.exists(self.socketfile):
                raise

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socketfile)
        self.server.listen(1)

        self.shellfile = "{}/{}.sh".format(self.cwd, self.label)  # the shellfile that will be submitted
        self.runfile = "{}/{}.run".format(self.cwd, self.label)  # the runfile created by the job
        self.submit.create_job(label=self.label, cwd=self.cwd, env=self.env, socketfile=self.socketfile, **kwargs)

    def run(self, **kwargs):
        self.create_job(**kwargs)
        self.jobid = self.submit.submit_job()

    def accept(self):
        """
        accept incoming connection from client
        this function is blocking
        """
        self.connection, client_address = self.server.accept()  # actual blocking statement
        return self.connection, client_address

    def recv(self, size=1024):
        """

        Returns
        -------

        """
        return self.connection.recv(size).decode()

    def send(self, data):
        self.connection.sendall(data.encode())
    def clean(self, args='so'):
        self.connection.close()
        os.unlink(self.socketfile)
        if args == 'all':
            args = 'so'
        if os.path.exists(self.shellfile) and 's' in args:
            os.remove(self.shellfile)
        if os.path.exists(self.runfile) and 'o' in args:
            os.remove(self.runfile)

class INET_Dispatcher(SH_Dispatcher):
    """
    AF INET Dispatcher utilizing sockets
    handles submitting the script to a Runner/Worker object
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.socket = None

    def create_job(self, **kwargs):
        super().init_run(**kwargs)
        host = socket.gethostname() #string, can be provided to bind.
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.bind((host, 0)) # let OS determine the port
        self.sockname = _socket.getsockname()
        self.socket = _socket
        self.socket.listen(1) # one server <-> one client
        self.shellfile = "{}/{}.sh".format(self.cwd, self.label)  # the shellfile that will be submitted
        self.runfile = "{}/{}.run".format(self.cwd, self.label)  # the runfile created by the job
        self.submit.create_job(label=self.label, cwd=self.cwd, env=self.env, sockname=self.sockname, **kwargs)
        self.connection = None

    def submit_job(self):
        self.jobid = self.submit.submit_job()
    def run(self, **kwargs):
        self.create_job(**kwargs)
        self.jobid = self.submit.submit_job()

    def accept(self):
        """
        accept incoming connection from runner
        this function is blocking
        """
        self.connection, peer_address = self.socket.accept()  # actual blocking statement
        return self.connection, peer_address

    def recv(self, size=1024):
        """

        Returns
        -------

        """
        return self.connection.recv(size).decode()

    def send(self, data):
        self.connection.sendall(data.encode())
    def clean(self, args='so'):
        if args == 'all':
            args = 'so'
        if self.socket:
            self.socket.close()
        if os.path.exists(self.shellfile) and 's' in args:
            os.remove(self.shellfile)
        if os.path.exists(self.runfile) and 'o' in args:
            os.remove(self.runfile)
