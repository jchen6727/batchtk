#from batchtk.algos import optuna_search
from batchtk.utils import TOTPConnection, TomlParser, expand_path
from batchtk.runtk import LocalDispatcher
from batchtk.utils import expand_path
from batchtk.runtk.trial import trial, LABEL_POINTER, DIR_POINTER


parser = TomlParser(file_path='expanse.toml')
Submit = parser.get_submit_class()
print(Submit())
config = {'x0': 5,
          'x1': 5,
          'label': LABEL_POINTER,
          'dir': DIR_POINTER}

results = trial(
    config=config,
    label='rosenbrock',
    tid=0,
    dispatcher_constructor=LocalDispatcher,
    submit_constructor=Submit,
    interval=10,
    project_dir=expand_path('.'),
    output_dir=expand_path('./output', create_dirs=True),
)
