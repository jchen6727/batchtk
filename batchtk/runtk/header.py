import json
import ast
from collections import namedtuple
import numpy

GREPSTR = 'RUNTK'
DELIM = '.'
SUBMIT = 'submit'
STDOUT = 'stdout'

STATUS = namedtuple('status', ['NOTFOUND', 'PENDING', 'RUNNING', 'COMPLETED', 'ERROR'])(1,2,3,4,5)
#NOTE: changing the second value will change the environment variable name and is SAFE(?)
# changing the 1st value will require a code refactor since it is referenced codewise in getattribute

STATUS_HANDLES = {
    STATUS.NOTFOUND: 'NOTFOUND',
    STATUS.PENDING: 'PENDING',
    STATUS.RUNNING: 'RUNNING',
    STATUS.COMPLETED: 'COMPLETED',
}


MSGOUT, MSGOUT_ENV = 'write_file' , 'MSGFILE'
SGLOUT, SGLOUT_ENV = 'signal'     , 'SGLFILE'
SOCKET, SOCKET_ENV = 'socket_name', 'SOCNAME'
JOBID , JOBID_ENV  = 'jobid'      , 'JOBID'

SOCKET_ALIASES = {SOCKET: SOCKET_ENV,
                  JOBID: JOBID_ENV}
FILE_ALIASES = {SGLOUT: SGLOUT_ENV,
                MSGOUT: MSGOUT_ENV,
                JOBID : JOBID_ENV}

COMM_HANDLES = {SUBMIT: 'runtk.SUBMIT',
           STDOUT: 'runtk.STDOUT',
           MSGOUT: 'runtk.MSGOUT',
           SGLOUT: 'runtk.SGLOUT',
           SOCKET: 'runtk.SOCKET',
}

SUPPORTS = { #TODO numpy handling? or binary serialization?
    'INT': int,
    'FLOAT': float,
    'JSON': ast.literal_eval, #use ast.literal_eval instead of eval to avoid executing malicious code
    'DICT': ast.literal_eval, #json.loads?
    'STR': staticmethod(lambda val: val),
    'LIST': ast.literal_eval, #TODO ast.literal_eval for each entry?
    'TUPLE': ast.literal_eval,
    'FLOAT64': float, #TODO what method encapsulate all other data type, 
    'INT64': int,
}

EXTENSIONS = { #anything that can be found in a path name to be included.
    SUBMIT: r'[a-zA-Z0-9\{\}_/\.]*\.[a-z]*sh', # sh, bash, csh, zsh, tcsh, etc. ask a sysadmin how they'd do this.
    STDOUT: r'[a-zA-Z0-9\{\}_/\.]*\.run',
    MSGOUT: r'[a-zA-Z0-9\{\}_/\.]*\.out',
    SGLOUT: r'[a-zA-Z0-9\{\}_/\.]*\.sgl', #TODO more like a lock file, would https://github.com/harlowja/fasteners be relevant?
    SOCKET: r'(\{sockname\})',
} # standardize names between EXTENSIONS and ALIASES?
