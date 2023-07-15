import os
import subprocess
import json
import hashlib
from .utils import convert, set_map, create_script
from .template import sge_template


#TODO logger support
class Dispatcher(object):
# Dispatcher calls some runner python script
    #cmdstr = "python runner.py"
    #cmdstr = "mpiexec -n {} nrniv -python -mpi {}".format( 1, 'runner.py' )
    grepstr = 'PMAP'
    id = None
    env = {}
    def __init__(self, cmdstr=None, grepstr=None, env={}):
        if cmdstr:
            self.cmdstr = cmdstr
        if grepstr:
            self.grepstr = grepstr
        if env:
            self.env = env
        self.id = hashlib.md5(self.env.encode()).hexdigest()
        self.cmdarr = self.cmdstr.split()
        # need to copy environ or else cannot find necessary paths.
        self.__osenv = os.environ.copy()
        self.__osenv.update(env)

        if self.savekey:
            filevar = env[self.savekey].split('=')[-1].strip()
            self.filename = "{}".format(filevar)

    def get_command(self):
        return self.cmdstr

    def run(self):
        self.proc = subprocess.run(self.cmdarr, env=self.__osenv, text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        return self.stdout, self.stderr

    def shrun(self, sh="qsub", template=sge_template, **kwargs):
        """
        instead of directly calling run, create and submit a shell script based on a custom template and 
        kwargs

        template: template of the script to be formatted
        kwargs: keyword arguments for template, must include unique {name}
            name: name for .sh, .run, .err files
        """
        filestr = kwargs['name'] = "{}_{}".format(kwargs['name'], self.id)
        self.watchfile = "{}.sgl".format(filestr)
        self.readfile  = "{}.out".format(filestr)
        shellfile = "{}.sh".format(filestr)
        create_script(env=self.env, filename=shellfile, template=template, **kwargs)
        cmd = "{} {}".format(sh, shellfile).split()
        self.proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        return self.stdout, self.stderr
    
    def check_shrun(self):
        # if file exists, return data, otherwise return None
        if os.path.exists(self.watchfile):
            with open(self.readfile, 'r') as fptr:
                return fptr.read()
        return False         

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
        self.signalfile = self.mappings['SGLFILE']
        self.writefile = self.mappings['OUTFILE']

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




class Netpyne_Runner(Runner):
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

    def save(self):
        self.sim.saveData()
