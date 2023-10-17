### Submit class ###
import subprocess

def create_env(env):
    envstr = '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in env.items()])
    return envstr

class Submit(object):
    key_args = {'label', 'cwd', 'env'}

    def __init__(self, submit_template = str(), script_template = str()):
        self.submit_template = submit_template
        self.script_template = script_template
        self.job = dict()
        self.script_path = str()
        self.job_script = str()
        self.handles = dict()
        self.env = dict()
        self.kwargs = {key: "{" + key + "}" for key in self.key_args}

    def create_job(self, **kwargs):
        self.format_job(**kwargs)
        self.job_script = "{}.sh".format(self.script_path)
        fptr = open(self.job_script, 'w')
        fptr.write(self.job['script'])
        fptr.close()

    def format_job(self, **kwargs):
        mkwargs = self.kwargs | kwargs
        submit = self.submit_template.format(**mkwargs)
        script = self.__format__(**mkwargs)
        self.job = {'submit': submit, 'script': script}
        self.script_path = "{cwd}/{label}".format(**mkwargs)
        self.label = mkwargs['label']
        return self.job

    def __repr__(self):
        self.format_job()
        reprstr = """\
submit:
\t{submit}
script: 
----------------------------------------------
{script}----------------------------------------------
""".format(**self.job)
        return reprstr

    def submit_job(self):
        subprocess.Popen(self.job['submit'].split(), )
        self.proc = subprocess.run(self.job['submit'].split(' '), text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        return 1

    def update_template(self, **kwargs):
        self.script_template = self.__format__(**kwargs)

    def __format__(self, **kwargs):
        mkwargs = self.kwargs | kwargs
        if isinstance(mkwargs['env'], dict):
            env = mkwargs['env']
            mkwargs['env'] = '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in env.items()])
        return self.script_template.format(**mkwargs)

    def format(self, **kwargs):
        return self.__format__(**kwargs)

    def create_handles(self, **kwargs):
        self.handles.update(kwargs)
        return self.handles

class SGESubmit(Submit):
    key_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', }
    template = \
        """\
#!/bin/bash
#$ -N j{label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export JOBID=$JOB_ID
{env}
{command}
"""
    def __init__(self):
        super().__init__(submit_template = "qsub {cwd}/{label}.sh", script_template = self.template)

    def create_job(self, **kwargs):
        self.format_job(**kwargs)
        self.job_script = "{}.sh".format(self.script_path)
        fptr = open(self.job_script, 'w')
        fptr.write(self.job['script'])
        fptr.close()

    def submit_job(self):
        super().submit_job()
        self.job_id = self.proc.stdout.split(' ')[2]
        return self.job_id

    def set_handles(self):
        pass

class SGESubmitSFS(SGESubmit):
    key_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', }
    template = \
        """\
#!/bin/bash
#$ -N j{label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export OUTFILE="{label}.out"
export SGLFILE="{label}.sgl"
export JOBID=$JOB_ID
{env}
{command}
"""

class SGESubmitINET(SGESubmit):
    key_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', 'ip', 'port'}
    template = \
        """\
#!/bin/bash
#$ -N j{label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export SOCIP="{ip}"
export SOCPORT="{port}"
{env}
{command}
"""
