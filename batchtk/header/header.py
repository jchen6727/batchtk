import ast
from enum import Enum

"""
ENVIRONMENT CONSTANTS
used in creating and extracting values from the environment
"""
GREPSTR = 'RUNTK' #string highlighting relevant environment variables for runner process
DELIM = '.' #delimiter for nesting environment variables (similar to "__getattribute__()" python method)
EQDELIM = '*=' #delimiter for assigning environment variables
"""
STATUS HANDLING -> see runtk/dispatchers.py
used in communicating the status of a job
"""
class STATUS(Enum):
    NOTFOUND = 1   #submit script not found, job not submitted
    PENDING = 2    #submit script found, job submitted but pending execution by remote scheduler
    RUNNING = 3    #message file found, job running on remote scheduler
    COMPLETED = 4  #signal file found, job completed successfully
    ERROR = 5      #to be implemented

"""
HANDLES W/ ALIASES -> see dispatchers.py, runners.py
used for environment variables relevant for Dispatcher -> Runner communication
i.e. make sure that MSGFILE, SGLFILE, SOCNAME, JOBID are assigned in the relevant Submit
"""
MSGOUT, MSGOUT_ENV = 'write_file'  , 'MSGFILE'
SGLOUT, SGLOUT_ENV = 'signal_file' , 'SGLFILE'
SOCKET, SOCKET_ENV = 'socket_name' , 'SOCNAME'
JOBID ,  JOBID_ENV = 'job_id'      , 'JOBID'
"""
 ^ ^ ^
 | | | 
 v v v
"""
SOCKET_ALIASES = \
    {SOCKET: SOCKET_ENV,
     JOBID: JOBID_ENV}
FILE_ALIASES   = \
    {SGLOUT: SGLOUT_ENV,
     MSGOUT: MSGOUT_ENV,
     JOBID : JOBID_ENV}

"""
ADDN. CONSTANT REFERENCES, 
custom string values to prevent value clashing (e.g. runtk.SUBMIT == runtk.STATUS.NOTFOUND)
"""
SUBMIT = 'submit'
STDOUT = 'stdout'

HANDLES = {SUBMIT: 'runtk.SUBMIT',
           STDOUT: 'runtk.STDOUT',
           MSGOUT: 'runtk.MSGOUT',
           SGLOUT: 'runtk.SGLOUT',
           SOCKET: 'runtk.SOCKET',
}

SOCKET_HANDLES = {SUBMIT: '{output_path}/{label}.sh',
                  STDOUT: '{output_path}/{label}.run',
                  SOCKET: '{sockname}'
                  }

FILE_HANDLES   = {SUBMIT: '{output_path}/{label}.sh',
                  STDOUT: '{output_path}/{label}.run',
                  MSGOUT: '{output_path}/{label}.out',
                  SGLOUT: '{output_path}/{label}.sgl'}

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
    SUBMIT: '[a-zA-Z0-9\{\}_/\.]*\.[a-z]*sh', # sh, bash, csh, zsh, tcsh, etc. ask a sysadmin how they'd do this.
    STDOUT: '[a-zA-Z0-9\{\}_/\.]*\.run',
    MSGOUT: '[a-zA-Z0-9\{\}_/\.]*\.out',
    SGLOUT: '[a-zA-Z0-9\{\}_/\.]*\.sgl', #TODO more like a lock file, would https://github.com/harlowja/fasteners be relevant?
    SOCKET: '(\{sockname\})',
} # standardize names between EXTENSIONS and ALIASES?


