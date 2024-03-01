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

EXTENSIONS = { #making crusty sysadmins cry
    'submit': '([\S]*\.[a-z]*sh)', # sh, bash, csh, zsh, tcsh, etc.
    'stdout': '([\S]*\.run)',
    'msgout': '([\S]*\.out)',
    'signal': '([\S]*\.sgl)',
    'socket': '([\S]*\.soc)',
}
