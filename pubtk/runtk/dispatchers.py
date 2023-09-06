import os
import subprocess
import hashlib
from .utils import convert, set_map, create_script
from .template import sge_template

class Group(object):
    obj_list = [] # each dispatcher object added to this list
    count = 0 # persistent count
    def __init__(self, obj):
        self.obj = obj

    def new(self, **kwargs):
        kwargs['id'] = self.count
        _obj = self.obj( **kwargs )
        self.obj_list.append(_obj)
        self.count = self.count + 1
        return _obj

    def __getitem__(self, i):
        return self.obj_list[i]

class Dispatcher(object):
    """
    base class for Dispatcher
    handles submitting the script to a Runner/Worker object and retrieving outputs
    """ 
    grepstr = 'PMAP' # the string ID for subprocess to identify necessary environment variables
    env = {} # string to store environment variables
    name = "" # dispatcher name, used to generate labels
    id = "" # dispatcher id, for instance the ADDR or CWD of the dispatcher
    uid = "" # unique id of dispatcher / worker pair.
    path = "" # location of dispatcher (path of dispatcher)
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
        ustr = str(self.id) + str(self.cmdstr) + str(self.env)
        self.uid = hashlib.md5(ustr.encode()).hexdigest()
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
        self.runfile   = "{}{}.run".format(self.cwd, filestr)
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
