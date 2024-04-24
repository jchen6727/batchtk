### Submit class ###
import subprocess
import logging
from collections import namedtuple
from batchtk import runtk
import re
from batchtk.utils import path_open
import os

SOCKET_HANDLES = {runtk.SUBMIT: '{output_path}/{label}.sh',
                  runtk.STDOUT: '{output_path}/{label}.run',
                  runtk.SOCKET: '{sockname}'
                  }

FILE_HANDLES   = {runtk.SUBMIT: '{output_path}/{label}.sh',
                  runtk.STDOUT: '{output_path}/{label}.run',
                  runtk.MSGOUT: '{output_path}/{label}.out',
                  runtk.SGLOUT: '{output_path}/{label}.sgl'}
class Template(object):

    def __new__(cls, template = None, key_args = None, **kwargs):
        if isinstance(template, Template):
            return template
        else:
            return super().__new__(cls)

    def __init__(self, template, key_args = None, **kwargs):
        if isinstance(template, Template): # passthrough if already a Template
            return #TODO why does this need to be here?, __init__ shouldn't be called if template
        self.template = template
        if key_args:
            self.kwargs = {key: "{" + key + "}" for key in key_args}
        else:
            self.kwargs = {key: "{" + key + "}" for key in self.get_args()}

    def get_args(self):
        return re.findall(r'{(.*?)}', self.template)

#    def __format__(self, **kwargs):
#        mkwargs = self.kwargs | kwargs
#        return self.template.format(mkwargs)

    def format(self, **kwargs):
        """
        formats the template with the supplied kwargs, returns the formatted string. The template value itself is
        unchanged
        :param kwargs:
        :return self.template.format(**kwargs) (str): template string formatted with kwargs.
        """
        mkwargs = self.kwargs | kwargs
        try:
            return self.template.format(**mkwargs)
        except KeyError as e:
            mkwargs = mkwargs | {key: "{" + key + "}" for key in self.get_args()}
            return self.template.format(**mkwargs)

    def update(self, **kwargs):
        """
        permanently updates the template with the supplied kwargs, returns None (template updated in place)
        :param kwargs:
        :return None:
        """
        self.template = self.format(**kwargs)

    def check_missing(self, template):
        """
        checks for missing keys in the provided template
        use, for instance as
        self.check_missing(self.format(**kwargs)) to validate that the format string completes successfully.
        :param template:
        :return:
        """
        return [key for key in self.kwargs if key in template]


    def __repr__(self):
        return self.template

    def __call__(self, **kwargs):
        return self.format(**kwargs)


serializers = {
    'sh': lambda x: '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in x.items()]),
    'eq': lambda x: ("".join(["{}={}\n".format(key, val) for key, val in x.items()]))[:-1], #rstrip the last newline
}

deserializers = {
    'eq': lambda x: dict([tuple(x.split('=')) for x in x.split('\n')]),
}

def serialize(args, var ='env', serializer ='sh'):
    if var in args and serializer in serializers:
        args[var] = serializers[serializer](args[var])
    return args # not necessary to return


class Submit(object):
    def __init__(self, submit_template, script_template, path_template=None, handles=None, log=None, **kwargs):
        self._jtuple = namedtuple('job', 'submit script path handles')
        self.submit_template = Template(submit_template)
        self.script_template = Template(script_template)
        self.path_template = path_template or Template(self.submit_template.template.split(' ')[-1])
        self.kwargs = self.submit_template.kwargs | self.script_template.kwargs | self.path_template.kwargs
        if handles: #TODO need better serialization of handles
            self.handles = Template(serializers['eq'](handles), key_args=self.kwargs)
        else:
            handles = self.create_handles()
            self.handles = Template(serializers['eq'](handles), key_args=self.kwargs)
        self.templates = self._jtuple(self.submit_template, self.script_template, self.path_template, self.handles)
        self.job = None
        self.submit = None
        self.script = None
        self.path = None
        self.logger = log
        if isinstance(log, str): ## TODO move into a logging object, then inherit?.
            self.logger = logging.getLogger(log)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler("{}.log".format(log))
            formatter = logging.Formatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        if isinstance(log, logging.Logger):
            pass

    def create_handles(self):
        handles = {}
        for extension, expr in runtk.EXTENSIONS.items():
            for template in [self.script_template, self.path_template]:
                handle = re.search(expr, template.template)
                if handle:
                    handles[extension] = handle.group()
        return handles

    def repr_handles(self):
        repr = "{\n"
        self_handles = self.get_handles()
        for handle in runtk.HANDLES:
            if handle in self_handles:
                repr += '\t{}: "{}",\n'.format(runtk.HANDLES[handle], self_handles[handle])
        repr += "}"
        return repr

    def log(self, message, level='info'):
        if self.logger:
            getattr(self.logger, level)(message)

    def create_job(self, **kwargs):
        kwargs = serialize(kwargs, var = 'env', serializer = 'sh')
        job = self.format_job(**kwargs) # doesn't update the templates
        self.job = job
        self.submit = job.submit
        self.script = job.script
        self.path = job.path
        self.handles = job.handles
        try:
            with path_open(self.path, 'w') as fptr:
                fptr.write(self.script)
        except Exception as e:
            raise Exception("Failed to write script to file: {}\n{}".format(self.path, e))

    def format_job(self, **kwargs):
        """
        if self.job:
            templates = list(self.job)
        else:
            templates = self.templates
        """
        _jtuple = [template.format(**kwargs) for template in self.templates]
        return self._jtuple(*_jtuple)

    def update_templates(self, **kwargs):
        #kwargs = serialize(kwargs, var = 'env', serializer = 'sh')
        for template in self.templates:
            template.update(**kwargs)

    def __repr__(self):
        if self.job:
            ssph = self.job._replace(handles=self.repr_handles()) #submit, script, path, handles
        else:
            ssph = self.templates._replace(handles=self.repr_handles())
        return """
submit:
{}

script:
{}

path:
{}

handles:
{}

kwargs:
{}
""".format(*ssph, self.kwargs)

    def submit_job(self):
        self.proc = subprocess.run(self.job.submit.split(' '), text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return self.proc

    def check_job(self):
        for fmt, template in zip(self.job, self.templates):
            missing = template.check_missing(fmt)
            if missing:
                raise KeyError("Missing keys in {}: {}".format(fmt, missing))

    def __format__(self, template = False, **kwargs): #dunder method, (self, spec)
        template = template or self.script_template
        mkwargs = self.kwargs | kwargs
        return template.format(**mkwargs)

    def get_handles(self):
        if self.job:
            return deserializers['eq'](self.job.handles)
        else:
            return deserializers['eq'](self.handles.template)


#class SHSubmit(Submit):
    #so actually ZSH and SH for the purposes of this are the EXACT SAME...
    #interpreter = os.getenv('SHELL', '/bin/bash') # defaults to /bin/bash
    #pass #TODO implement submit that identifies user shell.



class SHSubmit(Submit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_path}
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = {
        runtk.STDOUT: '{output_path}/{label}.run',
        runtk.SUBMIT: '{output_path}/{label}.sh'}
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="sh {output_path}/{label}.sh",
                                       key_args={'project_path', 'output_path', 'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
        )
    def set_handles(self):
        pass

    def submit_job(self):
        proc = super().submit_job()
        try:
            self.job_id = int(proc.stdout)
        except Exception as e:
            raise(Exception("{}\nJob submission failed:\n{}\n{}\n{}\n{}".format(e, self.submit, self.script, proc.stdout, proc.stderr)))
        if self.job_id < 0:
            raise(Exception("Job submission failed:\n{}\n{}\n{}\n{}".format(self.submit, self.script, proc.stdout, proc.stderr)))
        return self.job_id

class SHSubmitSFS(SHSubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_path}
export OUTFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = FILE_HANDLES

class SHSubmitSOCK(SHSubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'sockname'}
    script_template = \
        """\
#!/bin/sh
cd {project_path}
export SOCNAME="{sockname}"
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = SOCKET_HANDLES

ZSHSubmitSOCK = SHSubmitSOCK
ZSHSubmitSFS = SHSubmitSFS
ZSHSubmit = SHSubmit
class SGESubmit(Submit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'cores', 'vmem', }
    script_template = \
        """\
#!/bin/bash
#$ -N j{label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {output_path}/{label}.run
cd {project_path}
source ~/.bashrc
export JOBID=$JOB_ID
{env}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run'}
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="qsub {output_path}/{label}.sh",
                                       key_args={'output_path',  'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
            )

    def submit_job(self, **kwargs):
        proc = super().submit_job()
        try:
            self.job_id = proc.stdout.split(' ')[2]
        except Exception as e:
            raise(Exception("{}\nJob submission failed:\n{}\n{}\n{}\n{}".format(e, self.submit, self.script, proc.stdout, proc.stderr)))
        return self.job_id

    def set_handles(self):
        pass

class SGESubmitSFS(SGESubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'cores', 'vmem', }
    script_template = \
        """\
#!/bin/bash
#$ -N j{label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {output_path}/{label}.run
cd {project_path}
source ~/.bashrc
export OUTFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"
export JOBID=$JOB_ID
{env}
{command}
"""
    script_handles = FILE_HANDLES

class SGESubmitSOCK(SGESubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'cores', 'vmem', 'sockname'}
    script_template = \
        """\
#!/bin/bash
#$ -N j{label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {output_path}/{label}.run
cd {project_path}
source ~/.bashrc
export SOCNAME="{sockname}"
export JOBID=$JOB_ID
{env}
{command}
"""
    script_handles = SOCKET_HANDLES

