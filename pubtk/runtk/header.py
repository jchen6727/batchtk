import json
from collections import namedtuple

GREPSTR = 'RUNTK'
SUPPORTS = {
    'INT': int,
    'FLOAT': float,
    'JSON': json.loads,
    'DICT': json.loads,
    'STR': staticmethod(lambda val: val),
}

ALIASES = namedtuple('ALIASES', 'SOCKET FILE')(
    {'socketname': 'SOCNAME',
     'jobid': 'JOBID'},
    {'signalfile': 'SGLFILE',
     'writefile': 'OUTFILE',
     'jobid': 'JOBID'})

EXTENSIONS = {
    'submit': '([\S]*\.[a-z]*sh)', # sh, bash, csh, zsh, tcsh, etc. ask a sysadmin how they'd do this.
    'stdout': '([\S]*\.run)',
    'msgout': '([\S]*\.out)',
    'signal': '([\S]*\.sgl)',
    'socketname': '(\{sockname\})',
} # standardize names between EXTENSIONS and ALIASES?
