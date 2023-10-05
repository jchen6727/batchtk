import os
import json
from .utils import convert, set_map, create_script
from .template import sge_template

class Runner(object):
    grepstr = 'PUBTK' # unique delimiter to select environment variables to map
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
        self.env = os.environ.copy()
        self.env.update(_testenv)
        #self.debug.append("grepstr = {}".format(grepstr))
        self.grepstr = grepstr
        self.grepfunc = staticmethod(lambda key: grepstr in key )
        self.greptups = {key: self.env[key].split('=') for key in self.env if
                         self.grepfunc(key)}
        self.debug.append(self.env)
        # readability, greptups as the environment variables: (key,value) passed by 'PMAP' environment variables
        # saved the environment variables TODO JSON vs. STRING vs. FLOAT
        self.mappings = {
            val[0].strip(): self._convert(key.split(grepstr)[0], val[1].strip())
            for key, val in self.greptups.items()
        }
        # export JSONPMAP0="cfg.settings={...}" for instance would map the {...} as a json to cfg.settings



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

    def __getattr__(self, k):
        aliases = {
            'signalfile': 'SGLFILE',
            'writefile': 'OUTFILE',
            'jobid': 'JOBID',
        }
        if k in self.env:
            return self.env[k]
        elif k in aliases:
            return self.env[aliases[k]]
        else:
            raise KeyError(k)

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
    netParams = object()
    cfg = object()
    def __init__(self, netParams=None, cfg=None):
        super().__init__(grepstr='PUBTK')
        self.netParams = netParams
        self.cfg = cfg

    def get_netParams(self):
        if self.netParams:
            return self.netParams
        else:
            from netpyne import specs
            self.netParams = specs.NetParams()
            return self.netParams

    def get_cfg(self):
        if self.cfg:
            return self.cfg
        else:
            from netpyne import specs
            self.cfg = specs.SimConfig()
            return self.cfg

    def set_mappings(self, filter=''):
        for assign_path, value in self.mappings.items():
            if filter in assign_path:
                set_map(self, assign_path, value)
