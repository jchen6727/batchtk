import os
import json
from .utils import convert, set_map, create_script
from .template import sge_template

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
        if 'SGLFILE' in self.env:
            self.signalfile = self.env['SGLFILE']
        if 'OUTFILE' in self.env:
            self.writefile = self.env['OUTFILE']

    def get_debug(self):
        return self.debug

    def get_mappings(self):
        return self.mappings
    
    def write(self, data):
        fptr = open(self.writefile, 'w')
        fptr.write(data)
        fptr.close()

    def signal(self):
        open(self.signalfile, 'w').close()
                
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
    def __init__(self, netParams=None, cfg=None, sim=None):
        super().__init__(grepstr='NETM')
        if sim:
            self.sim = sim
        else:
            from netpyne import sim
            self.sim = sim
        if netParams:
            self.netParams = netParams
        else:
            from netpyne import specs
            self.netParams = specs.NetParams()
        if cfg:
            self.cfg = cfg
        else:
            from netpyne import specs
            self.cfg = specs.SimConfig()

    def set_mappings(self, filter=''):
        for assign_path, value in self.mappings.items():
            if filter in assign_path:
                set_map(self, assign_path, value)

    def create_params(self):
        pass

    def create(self):
        self.sim.create(self.netParams, self.cfg)

    def simulate(self):
        self.sim.simulate()

    def save(self):
        self.sim.saveData()

