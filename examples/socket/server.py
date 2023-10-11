from pubtk.runtk.dispatchers import AFU_Dispatcher
from pubtk.runtk.submit import Submit

template = """\
#!/bin/zsh
source ~/.zshrc
conda activate netpyne
cd {cwd}
export SOCFILE="{cwd}/{label}.s"
{env}
python client.py
"""

import os

cwd = os.getcwd()

def run(env):
    shrun = Submit(submit_template = "zsh {cwd}/{label}.sh", script_template = template)
    dispatcher = AFU_Dispatcher(cwd = cwd, env = env, submit = shrun)
    dispatcher.run()
    dispatcher.accept()
    data = dispatcher.recv()
    print(data)
    dispatcher.clean('so')
    return data

env = {'foo': 'bar'}
run(env)

#shrun = Submit(submit_template = "zsh {cwd}/{label}.sh", script_template = template)
#dispatcher = AFU_Dispatcher(cwd = cwd, env = env, submit = shrun)
#dispatcher.create_job()
