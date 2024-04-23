import json
from collections import namedtuple


GREPSTR = 'RUNTK'
SUBMIT = 'submit'
STDOUT = 'stdout'

#NOTE: changing the second value will change the environment variable name and is SAFE(?)
# changing the 1st value will require a code refactor since it is referenced codewise in getattribute

MSGOUT, MSGOUT_ENV = 'write_file' , 'MSGFILE'
SGLOUT, SGLOUT_ENV = 'signal'     , 'SGLFILE'
SOCKET, SOCKET_ENV = 'socket_name', 'SOCNAME'
JOBID , JOBID_ENV  = 'jobid'      , 'JOBID'

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

SOCKET_ALIASES = {SOCKET: SOCKET_ENV,
                  JOBID: JOBID_ENV}
FILE_ALIASES = {SGLOUT: SGLOUT_ENV,
                MSGOUT: MSGOUT_ENV,
                JOBID : JOBID_ENV}

EXTENSIONS = { #anything that can be found in a path name to be included.
    SUBMIT: '[a-zA-Z0-9\{\}_/\.]*\.[a-z]*sh', # sh, bash, csh, zsh, tcsh, etc. ask a sysadmin how they'd do this.
    STDOUT: '[a-zA-Z0-9\{\}_/\.]*\.run',
    MSGOUT: '[a-zA-Z0-9\{\}_/\.]*\.out',
    SGLOUT: '[a-zA-Z0-9\{\}_/\.]*\.sgl', #TODO more like a lock file, would https://github.com/harlowja/fasteners be relevant?
    SOCKET: '(\{sockname\})',
} # standardize names between EXTENSIONS and ALIASES?
