### Submit class ###
import subprocess
from collections import namedtuple

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

    def __repr__(self):
        return self.template

    def __call__(self):
        return self.template


serializers = {
    'sh': lambda x: '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in x.items()])
}
def serialize(args, var ='env', serializer ='sh'):
    if var in args and serializer in serializers:
        args[var] = serializers[serializer](args[var])
    return args # not necessary to return


class Submit(object):
    key_args = {'label', 'cwd', 'env'}

    def __init__(self, submit_template, script_template):
        self.submit_template = Template(submit_template)
        self.script_template = Template(script_template)
        self.path_template = Template("{cwd}/{label}.sh", {'cwd', 'label'})
        self.templates = {self.submit_template, self.script_template, self.path_template}
        self.kwargs = self.submit_template.kwargs | self.script_template.kwargs | self.path_template.kwargs
        self.job = None
        self.submit = None
        self.script = None
        self.path = None
        self.handles = None

    def create_job(self, **kwargs):
        kwargs = serialize(kwargs, var = 'env', serializer = 'sh')
        job = self.format_job(**kwargs) # doesn't update the templates
        self.job = job
        self.submit = job.submit
        self.script = job.script
        self.path = job.path
        fptr = open(self.path, 'w')
        fptr.write(self.script)
        fptr.close()

    def format_job(self, **kwargs):
        job = namedtuple('job', 'submit script path')
        submit = self.submit_template.format(**kwargs)
        script = self.script_template.format(**kwargs)
        path = self.path_template.format(**kwargs)
        return job(submit, script, path)

    def update_templates(self, **kwargs):
        kwargs = serialize(kwargs, var = 'env', serializer = 'sh')
        for template in self.templates:
            template.update(**kwargs)

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
        return self.proc


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
        proc = super().submit_job()
        self.job_id = proc.stdout.split(' ')[2]
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
