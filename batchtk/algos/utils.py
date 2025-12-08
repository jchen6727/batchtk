import hashlib
import json
import numpy


class Trial(object):
    pass
    def set_trial_args(self, ):



def _normalize(obj):
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_normalize(v) for v in obj]
    if isinstance(obj, numpy.ndarray):
        return _normalize(obj.tolist())
    if isinstance(obj, numpy.generic):
        return obj.item()
    return obj

def generate_tid_from_config(config: dict, length: int = 10, ignore_keys=None) -> str:
    """
    Produce a short alphanumeric id deterministically from `config`.
    - `ignore_keys` excludes keys from the hash.
    - `length` controls resulting hex length (default 10 chars).
    """
    ignore = set(ignore_keys or ())
    filtered = {k: v for k, v in config.items() if k not in ignore}
    normalized = _normalize(filtered)
    s = json.dumps(normalized, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:length]
