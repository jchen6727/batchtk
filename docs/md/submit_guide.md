The submit class is used to format, create and submit jobs.

batchtk uses the submit class in trial:

```Python
def trial(config: dict, label: str, tid: [str|int], dispatcher_constructor: callable, project_dir: str,
          output_dir: str, submit_constructor: callable, dispatcher_kwargs: Optional[dict] =None,
          submit_kwargs: Optional[dict] =None, interval: Optional[int]=60, data_storage: Optional[Storage]=None,
          debug_log: Optional[Logger|str]=None, report: Optional[list]=('path', 'config', 'data'), cleanup: Optional[bool|list|tuple] = (runtk.SGLOUT, runtk.MSGOUT), check_storage: Optional[bool]=True, **kwargs) -> pandas.Series:
```

Where submit_constructor takes a submit class and uses this within its runtime.
i.e.:

```Python
from batchtk.runtk
from batchtk.runtk.submit import SHSubmit # import base submit for executing scripts locally through the shell.
from batchtk.runtk.trial import trial # import trial function

class CustomSubmit(SHSubmit):
    script_args = {'label', 'project_dir', 'output_dir', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_dir}

{handles}

{env}
nohup {command} > {output_dir}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    handles = runtk.ALL_HANDLES

results = trial(submit_constructor=CustomSubmit, **kwargs) # executes 1 trial run in a separate shell process.
```

Any arbitrary string can be used for the `script_template`, though to establish the appropriate runtime environment and commmunication handling, the following
characteristics should be achieved by the script:

1. navigates to the project directory prior to execution of the command.
```shell
cd {project_dir}
```
2. establishes the appropriate communication handles prior to the execution of the command.
```shell
{handles}
```

3. establishes the appropriate environmental variables prior to the execution of the command.
```shell
{env}
```

4. calls the job such that it is executed in the background/asynchronously to the submit command.
```shell
nohup {command}
```

4a. on job submission engines, since the submit command simply queues the job, it is okay to call {command} without `nohup`

5. redirects standard output and error to the appropriate output files.
```shell
> {output_dir}/{label}.run 2>&1 &
```
