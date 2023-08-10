import os
import subprocess
import hashlib
from .utils import convert, set_map, create_script
from .template import sge_template

class Dispatcher(object):
    """
    base class for Dispatcher
    handles submitting the script to a Runner/Worker object and retrieving outputs
    """ 
    grepstr = 'PMAP' # the string ID for subprocess to identify necessary environment
    env = {} # environment 
    id = "" # dispatcher id, for instance the ADDR or CWD of the dispatcher
    uid = "" # unique id of dispatcher / worker pair.
    def __init__(self, id="", cmdstr=None, env={}):
        """
        initializes dispatcher
        id: string to identify dispatcher by the created runner
        cmdstr: the command to be run by the created runner
        env: any environmental variables to be inherited by the created runner 
        """
        if id:
            self.id = id
        if cmdstr:
            self.cmdstr = cmdstr
        if env:
            self.env = env
        self.uid = hashlib.md5(str(self.env).encode()).hexdigest()
        # need to copy environ or else cannot find necessary paths.
        self.__osenv = os.environ.copy()
        self.__osenv.update(env)

    def get_command(self):
        return self.cmdstr

    def run(self):
        self.proc = subprocess.run(self.cmdstr.split(), env=self.__osenv, text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        return self.stdout, self.stderr

class SFS_Dispatcher(Dispatcher):
    """
    Dispatcher utilizing shared file system
    handles submitting the script to a Runner/Worker object 
    """ 
    grepstr = 'PMAP' # the string ID for subprocess to identify necessary environment
    env = {} # environment 
    id = "" # dispatcher id, for instance the ADDR or CWD of the dispatcher
    uid = "" # unique id of dispatcher / worker pair.
    def __init__(self, cwd="", cmdstr=None, env={}):
        """
        initializes dispatcher
        id: string to identify dispatcher by the created runner
        cmdstr: the command to be run by the created runner
        env: any environmental variables to be inherited by the created runner 
        """
        super().__init__(id= cwd + '/', cmdstr=cmdstr, env=env)
        self.cwd=self.id

    def shrun(self, sh="qsub", template=sge_template, **kwargs):
        """
        instead of directly calling run, create and submit a shell script based on a custom template and 
        kwargs

        template: template of the script to be formatted
        kwargs: keyword arguments for template, must include unique {name}
            name: name for .sh, .run, .err files
        """
        kwargs['cwd'] = self.cwd
        filestr = kwargs['name'] = "{}_{}".format(kwargs['name'], self.uid)
        self.watchfile = "{}{}.sgl".format(self.cwd, filestr)
        self.readfile  = "{}{}.out".format(self.cwd, filestr)
        self.shellfile = "{}{}.sh".format(self.cwd, filestr)
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

    def clean(self, args='rsw'):
        if os.path.exists(self.readfile) and 'r' in args:
            os.remove(self.readfile)
        if os.path.exists(self.shellfile) and 's' in args:
            os.remove(self.shellfile)
        if os.path.exists(self.watchfile) and 'w' in args:
            os.remove(self.watchfile)

