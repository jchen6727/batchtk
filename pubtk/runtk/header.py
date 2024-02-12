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

ALIASES = {
    'SOCKET':
        {'socketname': 'SOCNAME',
         'jobid': 'JOBID'},
    'FILE':
        {'signalfile': 'SGLFILE',
         'writefile': 'OUTFILE',
         'jobid': 'JOBID'}
}