from pubtk.runtk.dispatchers import INET_Dispatcher
from pubtk.runtk.submit import Submit
import os


template = """\
#!/bin/zsh
source ~/.zshrc
conda activate netpyne
cd {cwd}
export SOCIP="{ip}"
export SOCPORT="{port}"
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
export SOCIP="{ip}"
export SOCPORT="{port}"
{env}
python client.py
"""

cwd = os.getcwd()

env = {'foo': 'bar'}

shrun = Submit(submit_template = "qsub {cwd}/{label}.sh", script_template = template)
dispatcher = INET_Dispatcher(cwd = cwd, env = env, submit = shrun)
dispatcher.create_job()
dispatcher.submit_job()
dispatcher.accept()
data = dispatcher.recv()
print("established connection")
print(data)
dispatcher.clean('so')


"""
shrun = Submit(submit_template = "zsh {cwd}/{label}.sh", script_template = template)
dispatcher = AFU_Dispatcher(cwd = cwd, env = env, submit = shrun)
dispatcher.create_job()
"""
