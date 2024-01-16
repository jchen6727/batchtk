### Submit class ###
import subprocess
from collections import namedtuple

serializers = {
    'sh': lambda x: '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in x.items()])
}
def create_exportstr(env):
    exportstr = '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in env.items()])
    return exportstr


class Template(object):

    def __new__(cls, template, key_args = None, **kwargs):
        if isinstance(template, Template):
            return template
        else:
            return super().__new__(cls)

    def __init__(self, template, key_args = None):
        if isinstance(template, Template): # passthrough if already a Template
            return
        self.template = template
        if key_args:
            self.kwargs = {key: "{" + key + "}" for key in key_args}
        else:
            self.kwargs = {key: "{" + key + "}" for key in self.get_args()}

    def get_args(self):
        import re
        return re.findall(r'{(.*?)}', self.template)

#    def __format__(self, **kwargs):
#        mkwargs = self.kwargs | kwargs
#        return self.template.format(mkwargs)

    def format(self, **kwargs):
        mkwargs = self.kwargs | kwargs
        try:
            return self.template.format(**mkwargs)
        except KeyError as e:
            mkwargs = mkwargs | {key: "{" + key + "}" for key in self.get_args()}
            return self.template.format(**mkwargs)

    def update(self, **kwargs):
        self.template = self.format(**kwargs)
        return self.template

    def __repr__(self):
        return self.template

    def __call__(self):
        return self.template


class Submit(object):
    key_args = {'label', 'cwd', 'env'}

    def __init__(self, submit_template, script_template):
        self.submit_template = Template(submit_template)
        self.script_template = Template(script_template)
        self.path_template = Template("{cwd}/{label}.sh", {'cwd', 'label'})
        self.kwargs = self.submit_template.kwargs | self.script_template.kwargs | self.path_template.kwargs
        self.job = None
        self.submit = None
        self.script = None
        self.path = None
        self.script_path = str()
        self.job_script = str()
        self.handles = dict()
        self.env = dict()

    def create_job(self, **kwargs):
        self.update_job(**kwargs)
        fptr = open(self.path, 'w')
        fptr.write(self.script)
        fptr.close()

    def format_job(self, **kwargs):
        job = namedtuple('job', 'submit script path label')
        submit = self.submit_template.format(**kwargs)
        script = self.script_template.format(**kwargs)
        path = self.path_template.format(**kwargs)
        if 'label' in kwargs:
            label = kwargs['label']
        else:
            label = '{label}'
        return job(submit, script, path, label)

    def update_job(self, **kwargs):
        job = namedtuple('job', 'submit script path label')
        self.update_templates(**kwargs)
        if 'label' in kwargs:
            self.label = kwargs['label']
        else:
            self.label = '{label}'
        self.job = job(self.submit, self.script, self.path, self.label)

    def __repr__(self):
        job = self.format_job()
        reprstr = \
            """\
submit:
----------------------------------------------
{submit}
script:
----------------------------------------------
{script}
----------------------------------------------
""".format(**job._asdict())
        return reprstr

    def submit_job(self):
        subprocess.Popen(self.job['submit'].split(), )
        self.proc = subprocess.run(self.job['submit'].split(' '), text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        return 1

    def update_submit(self, **kwargs):
        self.submit_template.update(**kwargs)
        self.submit = self.submit_template()

    def update_script(self, **kwargs):
        if 'env' in kwargs:
            kwargs['env'] = create_exportstr(kwargs['env'])
        self.script_template.update(**kwargs)
        self.script = self.script_template()

    def update_path(self, **kwargs):
        self.path_template.update(**kwargs)
        self.path = self.path_template()

    def update_templates(self, **kwargs):
        self.update_submit(**kwargs)
        self.update_script(**kwargs)
        self.update_path(**kwargs)

    def __format__(self, template = False, **kwargs): #dunder method, (self, spec)
        template = template or self.script_template
        mkwargs = self.kwargs | kwargs
        return template.format(**mkwargs)

    def create_handles(self, **kwargs):
        self.handles.update(kwargs)
        return self.handles

class SGESubmit(Submit):
    script_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', }
    script_template = \
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
        super().__init__(
            submit_template = Template(template="qsub {cwd}/{label}.sh", key_args={'cwd', 'label'}),
            script_template = Template(self.script_template, key_args=self.script_args))

    def submit_job(self):
        super().submit_job()
        self.job_id = self.proc.stdout.split(' ')[2]
        return self.job_id

    def set_handles(self):
        pass

class SGESubmitSFS(SGESubmit):
    script_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', }
    script_template = \
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
    script_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', 'socname'}
    script_template = \
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
    script_args = {'label', 'cwd', 'env', 'command', 'cores', 'vmem', 'sockname'}
    script_template = \
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
