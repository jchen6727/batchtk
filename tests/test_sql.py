from batchtk.utils import SQLiteLogger
from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.runtk.trial import trial
import os
log = SQLiteLogger(path='./test', entries={
    'label': 'TEXT', 'x0': 'TEXT', 'x1': 'TEXT', 'fx': 'TEXT'
})

submit = SHSubmitSFS()
submit.update_templates(command='python rosenbrock0_py.py')

path = "{}/runner_scripts".format(os.getcwd())

cfgs = [
    {'x0': 6, 'x1': 6},
    {'x0': 7, 'x1': 7},
    {'x0': 8, 'x1': 8},
]

for i, cfg in enumerate(cfgs):
    i = i + cfgs[0]['x0']
    data = trial(
        config=cfg,
        label='rosenbrock',
        tid=i,
        dispatcher_constructor=LocalDispatcher,
        project_path=path,
        output_path='./test_logs',
        submit=submit,
        dispatcher_kwargs=None,
        interval=1,
        log=log
    )
    print(data)

df = log.to_df()
print(df)
log.close()

