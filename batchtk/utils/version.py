import warnings
from batchtk import header

def update_locals(func_name: str, locals: dict, update_args: dict):
    """Update a dictionary of keyword arguments with new keyword arguments.

    Args:
        kwargs (dict): The original dictionary of keyword arguments.
        **new_kwargs: New keyword arguments to update the original dictionary.

    Returns:
        dict: The updated dictionary of keyword arguments.
    """
    updated_args = []
    for old, new in update_args.items():
        if old in locals:
            warnings.warn("method {}() argument {} deprecated in version: {}\nreplacing argument:\n\t{}={}\nto new argument:\n\t{}={} to be consistent with versioning changes".format(func_name, old, header.BATCHTK_VER, old, locals[old], new, locals[old]), DeprecationWarning)
        updated_args.append(locals[old])
    return updated_args

def test_update(testa=1, testb=2, testc=3, **kwargs):
    print(locals())
    testd, teste, testf = update_locals('test_update', locals(), {'testa': 'testd', 'testb': 'teste', 'testc': 'testf'})


test_update(testg = 3)