import os
import subprocess
import hashlib
from .utils import convert, set_map, create_script
from .template import sge_template
from .submit import Submit
import socket

class Dispatcher(object):
    """
    base class for Dispatcher
    handles submitting the script to a Runner/Worker object and retrieving outputs

    initialized values:
    env ->
        dictionary of values to be exported to the simulation environment, either within the subprocess call,
        or to an environment script
    grepstr ->
        the string value that allows the Runner class to identify relevant values
    gid ->
        a generated ID string that is unique to a Dispatcher <-> Runner pair.
    """ 
    obj_count = 0 # persistent count N.B. may be shared between objects.
    def __init__(self, env=None, grepstr='PUBTK', **kwargs):
        """
        Parameters
        ----------
        initializes dispatcher
        env - any environmental variables to be inherited by the created runner
        grepstr - the string ID for subprocess to identify necessary environment variables
        **kwargs is an unused placeholder

        initializes gid, the value will be created upon subprocess call.
        """
        self.env = {}
        if env:
            self.env.update(env)
        self.grepstr = grepstr
        self.gid = ''
        Dispatcher.obj_count = Dispatcher.obj_count + 1
        self.sid = id(self)


    def add_dict(self, dictionary, value_type='', **kwargs):
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
        cl = len(self.env)
        update = {"{}{}{}".format(value_type, self.grepstr, cl + i):
                      "{}={}".format(key, value) for i, (key, value) in enumerate(dictionary.items())}
        self.env.update(update)
        return update

    def add_val(self, value_type='', variable_path='', value='', **kwargs):
        """
        Parameters
        ----------
        value_type - the type of the value <val>
        variable_path - the path of the variable to map the value <val>
        value - the value

        adds an environment entry (self.env) specifying value -> variable_path
        Returns
        -------
        the entry added to the environment:
            {<value_type><self.grepstr><unique_id>: <variable_path><value>}
        """
        key = "{}{}{}".format(value_type, self.grepstr, len(self.env))
        item = "{}={}".format(variable_path, value)
        self.env[key] = item
        return {key: item}

    def init_run(self, **kwargs):
        """
        Parameters
        ----------
        **kwargs - of note, **kwargs here is used if necessary to help generate self.gid

        generates alphanumeric for self.gid based on self.env and **kwargs
        """
        gstr = str(self.env) + str(kwargs)
        self.gid = hashlib.md5(gstr.encode()).hexdigest()

class NOF_Dispatcher(Dispatcher):
    """
    No File Dispatcher, everything is run without generation of shell scripts.
    """
    def __init__(self, cmdstr='', env={}, **kwargs):
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
    def __init__(self, cwd="", submit=None, **kwargs):
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
        if submit:
            self.submit = submit
        else:
            self.submit = Submit()
        self.jobid = -1
        #self.label = self.gid

    def create_job(self, **kwargs):
        super().init_run()
        self.submit.create_job(label=self.gid,
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
        self.watchfile = "{}/{}.sgl".format(self.cwd, self.gid)  # the signal file (only to represent completion of job)
        self.readfile = "{}/{}.out".format(self.cwd, self.gid)  # the read file containing the actual results
        self.shellfile = "{}/{}.sh".format(self.cwd, self.gid)  # the shellfile that will be submitted
        self.runfile = "{}/{}.run".format(self.cwd, self.gid)  # the runfile created by the job
    def run(self, **kwargs):
        super().run(**kwargs)

    def get_run(self):
        # if file exists, return data, otherwise return None
        if os.path.exists(self.watchfile):
            fptr = open(self.readfile, 'r')
            data = fptr.read()
            fptr.close()
            return data
        return False

    def clean(self, args='rswo'):
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
    def create_job(self, **kwargs):
        super().create_job()
        self.socketfile = "{}/{}.s".format(self.cwd, self.gid)  # the socket file
        try:
            os.unlink(self.socketfile)
        except OSError:
            if os.path.exists(self.socketfile):
                raise

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socketfile)
        self.server.listen(1)

        self.shellfile = "{}/{}.sh".format(self.cwd, self.gid)  # the shellfile that will be submitted
        self.runfile = "{}/{}.run".format(self.cwd, self.gid)  # the runfile created by the job

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
        if os.path.exists(self.shellfile) and 's' in args:
            os.remove(self.shellfile)
        if os.path.exists(self.runfile) and 'o' in args:
            os.remove(self.runfile)

class INET_Dispatcher(SH_Dispatcher):
    """
    AF INET Dispatcher utilizing sockets
    handles submitting the script to a Runner/Worker object
    """
    def create_job(self, ports = (60000, 65535), **kwargs):
        super().init_run(**kwargs)
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        self.ip = ip
        port = ports[0]
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                server.bind((ip, port))
                break
            except:
                port = port + 1
                if port == ports[1]:
                    raise
        self.port = port
        self.server = server
        self.server.listen(1)
        self.shellfile = "{}/{}.sh".format(self.cwd, self.gid)  # the shellfile that will be submitted
        self.runfile = "{}/{}.run".format(self.cwd, self.gid)  # the runfile created by the job
        self.submit.create_job(label=self.gid, cwd=self.cwd, env=self.env, ip=self.ip, port=self.port, **kwargs)

    def submit_job(self):
        self.jobid = self.submit.submit_job()
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
        if os.path.exists(self.shellfile) and 's' in args:
            os.remove(self.shellfile)
        if os.path.exists(self.runfile) and 'o' in args:
            os.remove(self.runfile)
