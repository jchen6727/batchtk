import hashlib, zlib, uuid
import json
import numpy
from typing import Optional

import pandas
from batchtk import runtk
from batchtk.runtk import constructors
from batchtk import runtk
import json

class Trial(object):
    def set_fixed_trial_args(self,
                       dispatcher_constructor: callable = None, project_dir: str = None,
                       output_dir: str = None, submit_constructor: callable = None,
                       storage_dir: str = None, dispatcher_kwargs: Optional[dict] = None,
                       submit_kwargs: Optional[dict] = None, interval: Optional[int] = 60,
                       storage_constructor: Optional[callable] = constructors.SQLiteStorage,
                       storage_kwargs: Optional[dict] = None,
                       log_constructor: Optional[callable] = constructors.BatchtkLogger,
                       log_kwargs: Optional[dict] = None, report: Optional[list] = ('path', 'config', 'data'),
                       cleanup: Optional[bool | list | tuple] = (runtk.SGLOUT, runtk.MSGOUT),
                       check_storage: Optional[bool] = True,
                       ):
        self._fixed_trial_args = {
            'dispatcher_constructor': dispatcher_constructor, 'project_dir': project_dir,
            'output_dir': output_dir, 'submit_constructor': submit_constructor,
            'storage_dir': storage_dir, 'dispatcher_kwargs': dispatcher_kwargs,
            'submit_kwargs': submit_kwargs, 'interval': interval,
            'storage_constructor': storage_constructor, 'storage_kwargs': storage_kwargs,
            'log_constructor': log_constructor, 'log_kwargs': log_kwargs, 'report': report,
            'cleanup': cleanup, 'check_storage': check_storage
        }

    @staticmethod
    def compute_id_from_args(*args, **kwargs): # via fast CRC-32 checksum
        _s = ''
        for arg in args:
            if isinstance(arg, dict):
                _s += json.dumps(arg, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
            else:
                _s += str(arg)
        _s = _s + json.dumps(kwargs, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        bconfig = f"{_s}".encode('utf-8')
        idn = zlib.crc32(bconfig) & 0xFFFFFFFF
        return idn

    def run_trial(self, **kwargs):
        trial_args = self._fixed_trial_args | kwargs
        return runtk.trial(**trial_args)