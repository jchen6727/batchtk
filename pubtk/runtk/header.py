import json
from collections import namedtuple

GREPSTR = 'RUNTK'
SUBMIT = 'submit'
STDOUT = 'stdout'
MSGOUT = 'msgout'
SGLOUT = 'signal'
SOCKET = 'socketname'

HANDLES = {SUBMIT, STDOUT, MSGOUT, SGLOUT, SOCKET}

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
    SUBMIT: '([\S]*\.[a-z]*sh)', # sh, bash, csh, zsh, tcsh, etc. ask a sysadmin how they'd do this.
    STDOUT: '([\S]*\.run)',
    MSGOUT: '([\S]*\.out)',
    SGLOUT: '([\S]*\.sgl)', #TODO more like a lock file, would https://github.com/harlowja/fasteners be relevant?
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
"""

"""
DISPATCHERS = {
    'inet': INET_Dispatcher,
    'unix': UNIX_Dispatcher,
    'sfs': SFS_Dispatcher,
}
"""
