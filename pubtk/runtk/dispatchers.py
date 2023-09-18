import os
import subprocess
import hashlib
from .utils import convert, set_map, create_script
from .template import sge_template
from .submit import Submit
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

    def __init__(self, env={}, grepstr='PUBTK', **kwargs):
        """
        Parameters
        ----------
        initializes dispatcher
        env - any environmental variables to be inherited by the created runner
        grepstr - the string ID for subprocess to identify necessary environment variables
        **kwargs is an unused placeholder

        initializes gid, the value will be created upon subprocess call.
        """
        self.env = env
        self.grepstr = grepstr
        self.gid = ''

    def add_dict(self, value_type='', dictionary={}, **kwargs):
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
    def __init__(self, cwd="", env={}, submit=Submit(), **kwargs):
        """
        initializes dispatcher
        id: string to identify dispatcher by the created runner
        env: any environmental variables to be inherited by the created runner
        submit: Submit object (see pubtk.runk.submit)
        """
        super().__init__(env=env, **kwargs)
        self.cwd = cwd
        self.submit = submit
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
        super().init_run()
        self.submit.create_job(label=self.label, cwd=self.cwd, env=self.env, **kwargs)
        self.jobid = self.submit.submit_job()

class SFS_Dispatcher(SH_Dispatcher):
    """
    Shared File System Dispatcher utilizing file operations to submit jobs and collect results
    handles submitting the script to a Runner/Worker object
    """

    def create_job(self, **kwargs):
        super().init_run(**kwargs)
        self.watchfile = "{}/{}.sgl".format(self.cwd, self.label)  # the signal file (only to represent completion of job)
        self.readfile = "{}/{}.out".format(self.cwd, self.label)  # the read file containing the actual results
        self.shellfile = "{}/{}.sh".format(self.cwd, self.label)  # the shellfile that will be submitted
        self.runfile = "{}/{}.run".format(self.cwd, self.label)  # the runfile created by the job

class SFS_Dispatcher(SH_Dispatcher):
    """
    Shared File System Dispatcher utilizing file operations to submit jobs and collect results
    handles submitting the script to a Runner/Worker object 
    """
    env = {} # environment 
    id = "" # dispatcher id, for instance the ADDR or CWD of the dispatcher
    uid = "" # unique id of dispatcher / worker pair.
    def __init__(self, cwd="", env={}, submit=Submit(), **kwargs):
        """
        initializes dispatcher
        id: string to identify dispatcher by the created runner
        cmdstr: the command to be run by the created runner
        env: any environmental variables to be inherited by the created runner 
        """
        super().__init__(id= cwd, cmdstr=cmdstr, env=env, **kwargs)
        self.path=self.cwd=self.id

    def shcreate(self, template=sge_template, **kwargs):
        """
        instead of directly calling run, create and submit a shell script based on a custom template and 
        kwargs

        template: template of the script to be formatted
        kwargs: keyword arguments for template, must include unique {name}
            name: name for .sh, .run, .err files
        """
        kwargs['path']=kwargs['cwd'] = self.cwd
        filestr = kwargs['label'] = "{}_{}".format(kwargs['label'], self.uid)
        self.watchfile = "{}/{}.sgl".format(self.cwd, filestr) # the signal file (only to represent completion of job)
        self.readfile  = "{}/{}.out".format(self.cwd, filestr) # the read file containing the actual results
        self.shellfile = "{}/{}.sh".format(self.cwd, filestr)  # the shellfile that will be submitted
        self.runfile   = "{}/{}.run".format(self.cwd, filestr) # the runfile created by the job
        create_script(env=self.env, command=self.cmdstr, filename=self.shellfile, template=template, **kwargs)
        
    def shrun(self, sh="qsub", template=sge_template, **kwargs):
        """
        instead of directly calling run, create and submit a shell script based on a custom template and 
        kwargs

        template: template of the script to be formatted
        kwargs: keyword arguments for template, must include unique {name}
            name: name for .sh, .run, .err files
        """
        kwargs['path']=kwargs['cwd'] = self.cwd
        filestr = kwargs['label'] = "{}_{}".format(kwargs['label'], self.uid)
        self.watchfile = "{}/{}.sgl".format(self.cwd, filestr)
        self.readfile  = "{}/{}.out".format(self.cwd, filestr)
        self.shellfile = "{}/{}.sh".format(self.cwd, filestr)
        self.runfile   = "{}/{}.run".format(self.cwd, filestr)
        create_script(env=self.env, command=self.cmdstr, filename=self.shellfile, template=template, **kwargs)
        self.proc = subprocess.run([sh, self.shellfile], text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        return self.stdout, self.stderr
    
    def get_shrun(self):
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

class AFU_Dispatcher(Dispatcher):
    """
    AF UNIX Dispatcher utilizing sockets (still requires shared file system)
    handles submitting the script to a Runner/Worker object
    """
    pass
