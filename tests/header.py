"""
Notice
from pubtk.SUPPORTS
SUPPORTS = { #TODO numpy handling? or binary serialization?
    'INT': int,
    'FLOAT': float,
    'JSON': json.loads,
    'DICT': json.loads,
    'STR': staticmethod(lambda val: val),
    'LIST': ast.literal_eval, #TODO ast.literal_eval for each entry?
    'TUPLE': ast.literal_eval
}
"""

TEST_ENVIRONMENT = {
    'strvalue': '1',
    'intvalue': 2,
    'fltvalue': 3.0,
    #'dictvalue': {'key': 'value'}, #TODO serialization needs to json.dumps properly
    'listvalue': [1, 2.0, "3, 4, 5"],
}