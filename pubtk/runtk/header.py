import json
from collections import namedtuple

GREPSTR = 'RUNTK'
SUBMIT = 'submit'
STDOUT = 'stdout'
MSGOUT = 'msgout'
SGLOUT = 'signal'
SOCKET = 'socketname'

HANDLES = {SUBMIT: 'runtk.SUBMIT',
           STDOUT: 'runtk.STDOUT',
           MSGOUT: 'runtk.MSGOUT',
           SGLOUT: 'runtk.SGLOUT',
           SOCKET: 'runtk.SOCKET'}

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

EXTENSIONS = { #anything that can be found in a path name to be included.
    SUBMIT: '[a-zA-Z0-9\{\}_/\.]*\.[a-z]*sh', # sh, bash, csh, zsh, tcsh, etc. ask a sysadmin how they'd do this.
    STDOUT: '[a-zA-Z0-9\{\}_/\.]*\.run',
    MSGOUT: '[a-zA-Z0-9\{\}_/\.]*\.out',
    SGLOUT: '[a-zA-Z0-9\{\}_/\.]*\.sgl', #TODO more like a lock file, would https://github.com/harlowja/fasteners be relevant?
    SOCKET: '(\{sockname\})',
} # standardize names between EXTENSIONS and ALIASES?

"""
RUNNERS = {
    'socket': SocketRunner,
    'inet': SocketRunner,
    'unix': SocketRunner,
    'file': FileRunner,
    's': SocketRunner,
    'f': FileRunner,
}

[tuple(x.split('=')) for x in self.handles.template.split('\n')]
"""

"""
DISPATCHERS = {
    'inet': INET_Dispatcher,
    'unix': UNIX_Dispatcher,
    'sfs': SFS_Dispatcher,
}
"""
