from batchtk.utils import SQLiteLogger
from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.runtk.trial import trial
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

log = SQLiteLogger(path='./test_logs', entries=['x0', 'x1', 'fx'])

cfgs = [
    {'x0': 0, 'x1': 0},
    {'x0': 1, 'x1': 1},
    {'x0': 2, 'x1': 2},
]

#submit = SHSubmitSFS()
#submit.update_templates(command='python rosenbrock0_py.py')

path = "{}/runner_scripts".format(os.getcwd())

def run_trial(cfg):
    return trial(
        config=cfg,
        label='rosenbrock',
        tid="{}_{}".format(cfg['x0'], cfg['x1']),
        dispatcher_constructor=LocalDispatcher,
        project_path=path,
        output_path='../test_logs',
        submit_constructor=SHSubmitSFS,
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'python rosenbrock0_py.py'},
        interval=1,
        log=log
    )

results = []
with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit all trials to the executor
    future_to_cfg = {executor.submit(run_trial, cfg): cfg for cfg in cfgs}

    # Collect results as they complete
    for future in as_completed(future_to_cfg):
        cfg = future_to_cfg[future]
        try:
            result = future.result()
            results.append(result)
            print(result)
        except Exception as e:
            print(f"Trial for config {cfg} failed with exception: {e}")

df = log.to_df()
print(df)
log.close()

