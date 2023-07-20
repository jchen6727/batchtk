import os
import subprocess
import json
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
        self.bashfile = "{}{}.sh".format(self.cwd, filestr)
        create_script(env=self.env, command=self.cmdstr, filename=self.shellfile, template=template, **kwargs)
        self.proc = subprocess.run([sh, self.bashfile], text=True, stdout=subprocess.PIPE, \
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
        if os.path.exists(self.bashfile) and 's' in args:
            os.remove(self.bashfile)
        if os.path.exists(self.watchfile) and 'w' in args:
            os.remove(self.watchfile)


class Runner(object):
    grepstr = 'PMAP' # unique delimiter to select environment variables to map
    # the datatype is can be defined before the grepstr
    # e.g. FLOATPMAP or STRINGPMAP
    _supports = { # Python > 3.6, dictionaries keep keys in order they were created, 'FLOAT' -> 'JSON' -> 'STRING'
        'FLOAT': float,
        'JSON': json.loads, #NB TODO? JSON is loaded in reverse order
        'STRING': staticmethod(lambda val: val),
    }
    mappings = {}# self.mappings keys are the variables to map, self.maps[key] are values supported by _supports
    debug = []# list of debug statements: self.debug.append(statement)
    signalfile = None
    writefile = None
    def __init__(
        self,
        grepstr='PMAP',
        _testenv={}
    ):
        if not _testenv:
            self.env = os.environ
        else:
            self.env = _testenv
        #self.debug.append("grepstr = {}".format(grepstr))
        self.grepstr = grepstr
        self.grepfunc = staticmethod(lambda key: grepstr in key )
        self.greptups = {key: self.env[key].split('=') for key in self.env if
                         self.grepfunc(key)}
        self.debug.append(os.environ)
        # readability, greptups as the environment variables: (key,value) passed by 'PMAP' environment variables
        # saved the environment variables TODO JSON vs. STRING vs. FLOAT
        self.mappings = {
            val[0].strip(): self._convert(key.split(grepstr)[0], val[1].strip())
            for key, val in self.greptups.items()
        }
        self.signalfile = self.env['SGLFILE']
        self.writefile = self.env['OUTFILE']

    def get_debug(self):
        return self.debug

    def get_mappings(self):
        return self.mappings


    def __getitem__(self, k):
        try:
            return object.__getattribute__(self, k)
        except:
            raise KeyError(k)

    def _convert(self, _type, val):
        return convert(self, _type, val)

class NetpyneRunner(Runner):
    """
    # runner for netpyne
    # see class runner
    mappings <-
    """
    sim = object()
    netParams = object()
    cfg = object()
    def __init__(self):
        super().__init__(grepstr='NETM')

    def set_mappings(self):
        for assign_path, value in self.mappings.items():
            set_map(self, assign_path, value)

    def create(self):
        self.sim.create(self.netParams, self.cfg)

    def simulate(self):
        self.sim.simulate()

    def write(self, data):
        fptr = open(self.writefile, 'w')
        fptr.write(data)
        fptr.close()        

    def save(self):
        self.sim.saveData()



#TODO logger support?