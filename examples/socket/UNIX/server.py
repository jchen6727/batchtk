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

template = """\
#!/bin/bash
#$ -N job{label}
#$ -pe smp 5
#$ -l h_vmem=32G
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export SOCFILE="{cwd}/{label}.s"
{env}
python client.py
"""


import os

cwd = os.getcwd()

env = {'foo': 'bar'}


def run(env):
    shrun = Submit(submit_template = "bash {cwd}/{label}.sh", script_template = template)
    dispatcher = AFU_Dispatcher(cwd = cwd, env = env, submit = shrun)
    dispatcher.run()
    dispatcher.accept()
    data = dispatcher.recv()
    print("called receive block")
    print(data)
    dispatcher.clean('so')
    return data


run(env)

"""
shrun = Submit(submit_template = "zsh {cwd}/{label}.sh", script_template = template)
dispatcher = AFU_Dispatcher(cwd = cwd, env = env, submit = shrun)
dispatcher.create_job()
"""
