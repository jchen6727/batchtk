### Submit class ###
import logging
from collections import namedtuple
from batchtk import runtk
import re

#TODO, encapsulate file system #DONE, encapsulate connection #DONE

class Template(object):
    """
    Class for Template objects
    """
    def __new__(cls, template = None, key_args = None, **kwargs):
        if isinstance(template, Template):
            return template # any template object can be passed through -> see __init__
        else:
            return super().__new__(cls)

    def __init__(self, template, key_args = None, **kwargs):
        if isinstance(template, Template): # passthrough if already a Template
            return
        self.template = template
        if key_args:
            self.key_args = {key: "{" + key + "}" for key in key_args}
        else:
            self.key_args = {key: "{" + key + "}" for key in self.get_args()}

    def get_args(self):
        return re.findall(r'{(.*?)}', self.template)

#    def __format__(self, **kwargs):
#        mkwargs = self.key_args | kwargs
#        return self.template.format(mkwargs)

    def format(self, **kwargs):
        """
        formats the template with the supplied kwargs, returns the formatted string. The template itself is
        unchanged
        :param kwargs:
        :return self.template.format(**kwargs) (str): template string formatted with kwargs.
        """
        mkwargs = self.key_args | kwargs
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
        return [key for key in self.key_args if key in template]


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


_Job = namedtuple('job', 'submit script path handles')

class Submit(object):
    def __init__(self, submit_template, script_template, path_template=None, handles=None, log=None, **kwargs):
        self.submit_template = Template(submit_template)
        self.script_template = Template(script_template)
        self.path_template = path_template or Template(self.submit_template.template.split(' ')[-1])
        self.key_args = self.submit_template.key_args | self.script_template.key_args | self.path_template.key_args
        if handles: #TODO need better serialization of handles
            self.handles = Template(serializers['eq'](handles), key_args=self.key_args)
        else:
            handles = self.create_handles()
            self.handles = Template(serializers['eq'](handles), key_args=self.key_args)
        self.templates = _Job(self.submit_template, self.script_template, self.path_template, self.handles)
        self.job = None
        self.submit = None
        self.script = None
        self.path = None
        self.proc = None
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

    def format_job(self, **kwargs):
        """
        if self.job:
            templates = list(self.job)
        else:
            templates = self.templates
        """
        _tuple = [template.format(**kwargs) for template in self.templates]
        return _Job(*_tuple)

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

key_args:
{}
""".format(*ssph, self.key_args)

    def deploy_job(self, fs=None):
        pass

    def submit_job(self, fs=None, cmd=None, check=False):
        if fs is None:
            from batchtk.utils import LocalFS
            fs = LocalFS()
        if cmd is None:
            from batchtk.utils import LocalProcCmd
            cmd = LocalProcCmd()
        if self.job is None:
            raise Exception("Job not created, call create_job() first")
        if check and fs.exists(self.path):
            return None
        try:
            with fs.path_open(self.path, 'w') as fptr:
                fptr.write(self.script)
        except Exception as e:
            raise Exception("Failed to write script to file: {}\n{}".format(self.path, e))
        self.proc = cmd.run(self.job.submit)
        return self.proc

    def check_job(self):
        for fmt, template in zip(self.job, self.templates):
            missing = template.check_missing(fmt)
            if missing:
                raise KeyError("Missing keys in {}: {}".format(fmt, missing))

    def __format__(self, template = False, **kwargs): #dunder method, (self, spec)
        template = template or self.script_template
        mkwargs = self.key_args | kwargs
        return template.format(**mkwargs)

    def get_handles(self):
        if self.job:
            return deserializers['eq'](self.job.handles)
        else:
            return deserializers['eq'](self.handles.template)

_default_submit = Template(template="sh {output_path}/{label}.sh",
                          key_args={'output_path', 'label'})

_default_script = Template(
    template= \
"""\
#!/bin/sh
cd {project_path}
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
""",
    key_args={'label', 'project_path', 'output_path', 'env', 'command'}
)

_default_handles = {
        runtk.STDOUT: '{output_path}/{label}.run',
        runtk.SUBMIT: '{output_path}/{label}.sh'}

class SHSubmit(Submit):
    def __init__(self,
                 submit_template = None,
                 script_template = None,
                 handles = None,
                 **kwargs):
        #check for class attributes first, then passed arguments, then default values
        submit_template = hasattr(self, 'submit_template') and self.submit_template or submit_template or _default_submit
        script_template = hasattr(self, 'script_template') and self.script_template or script_template or _default_script
        handles = hasattr(self, 'handles') and self.handles or handles or _default_handles
        super().__init__(
            submit_template = submit_template,
            script_template = script_template,
            handles = handles,
            **kwargs
        )
    def set_handles(self):
        pass

    def submit_job(self, **kwargs):
        proc = super().submit_job()
        try:
            self.job_id = int(proc.stdout)
        except Exception as e:
            raise(Exception("{}\nJob submission failed:\n{}\n{}\n{}\n{}".format(e, self.submit, self.script, proc.stdout, proc.stderr)))
        if self.job_id < 0:
            raise(Exception("Job submission failed:\n{}\n{}\n{}\n{}".format(self.submit, self.script, proc.stdout, proc.stderr)))
        return self.job_id

# reference classes used as examples and for testing.
#TODO make sure to
class SHSubmitSFS(SHSubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_path}
export MSGFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    handles = runtk.FILE_HANDLES

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
    handles = runtk.SOCKET_HANDLES
