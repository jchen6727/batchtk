### Submit class ###
import subprocess
from collections import namedtuple


def create_exportstr(env):
    exportstr = '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in env.items()])
    return exportstr

class Template(str):
    def __init__(self, template, key_args = False):
        self.template = template
        if key_args:
            self.kwargs = {key: "{" + key + "}" for key in key_args}
        else:
            self.kwargs = {key: "{" + key + "}" for key in self.get_args()}

    def get_args(self):
        import re
        return re.findall(r'{(.*?)}', self.template)

    def __format__(self, **kwargs):
        mkwargs = self.kwargs | kwargs
        return self.template.format(mkwargs)

    def format(self, **kwargs):
        return self.template.format(**kwargs)

    def update(self, **kwargs):
        self.template = self.format(**kwargs)

    def __repr__(self):
        return self.template

class Submit(object):
    key_args = {'label', 'cwd', 'env'}

    def __init__(self, submit_template = str(), script_template = str()):
        self.submit_template = Template(template = submit_template, key_args = self.key_args)
        self.script_template = Template(template = script_template, key_args = self.key_args)
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
        job = namedtuple('job', 'submit script path label')
        mkwargs = self.kwargs | kwargs
        submit = self.submit_template.format(**mkwargs)
        script = self.__format__(**mkwargs)
        path = "{cwd}/{label}.sh".format(**mkwargs)
        label = mkwargs['label']
        return job(submit, script, path, label)

    def __repr__(self):
        self.format_job()
        reprstr = \
            """\
submit:
----------------------------------------------
{submit}
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

    def update_submit(self, **kwargs):
        self.submit_template = self.format(self.submit_template, **kwargs)
    def update_script(self, **kwargs):
        if 'env' in kwargs:
            kwargs['env'] = create_exportstr(kwargs['env'])
        self.script_template = self.format(self.script_template, **kwargs)

    def update(self, **kwargs):
        self.update_submit(**kwargs)
        self.update_script(**kwargs)

    def __format__(self, template = False, **kwargs): #dunder method, (self, spec)
        template = template or self.script_template
        mkwargs = self.kwargs | kwargs
        return template.format(**mkwargs)

    def format_template(self, template, **kwargs):
        mkwargs = self.kwargs | kwargs
        return template.format(**mkwargs)

    def format_submit(self, **kwargs):
    def format_script(self, template, **kwargs):
        mkwargs = self.kwargs | kwargs
        return template.format(self.script_template, **mkwargs)

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

class SGESubmitSOCK(SGESubmit):
    key_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', 'socname'}
    template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export SOCNAME="{sockname}"
{env}
{command}
"""

class SGESubmitINET(SGESubmit):
    key_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', 'sockname'}
    template = \
        """\
#!/bin/bash
#$ -N {label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export SOCNAME="{sockname}"
{env}
{command}
"""
