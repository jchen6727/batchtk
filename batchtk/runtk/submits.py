### Submit class ###
import logging
from collections import namedtuple
from batchtk import runtk
from batchtk.utils import flush_fptr
import re
import warnings
from traceback import print_stack
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

    def __init__(self, template, key_args = None, **kwargs): # ensure idempotency with the first check
        if isinstance(template, Template): # passthrough if already a Template
            return # why is this necessary?
        # if a template is passed to __new__, it returns an instance of Template, therefore calling the __init__ function
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
            message = (
                f"Warning:"
                f"In Template.format({kwargs}): argument '{e.args}' was found in the script:"
                f"{self.template}"
                f"Recommend user provide '{e.args}' to Template.key_args or in kwargs."
                f"current self.key_args:\n{self.key_args}"
                f"see traceback:\n{print_stack(limit=5)}" # avoid recursion?
            )
            warnings.warn(message)
            self.key_args = {key: "{" + key + "}" for key in self.get_args()}
            mkwargs = self.key_args | kwargs
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
    def __init__(self, submit_template, script_template, path_template=None, handles=None, log=None,
                 key_args=('label', 'project_dir', 'output_dir', 'output_path', 'env', 'handles', 'socket_name', 'command', 'stdout', 'stderr', 'path'),
                 protected_args=('label', 'project_dir', 'output_dir', 'output_path', 'env', 'handles', 'socket_name', 'stdout', 'stderr', 'path'),
                 **kwargs):

        #key_args can be updated and formatted,
        #protected_args can only be formatted
        self.submit_template = Template(submit_template, key_args=key_args)
        self.script_template = Template(script_template, key_args=key_args)
        self.path_template = path_template or Template(self.submit_template.template.split(' ')[-1])
        self.key_args = self.submit_template.key_args | self.script_template.key_args | self.path_template.key_args
        self.protected_args = set(protected_args)
        handles = handles or self.create_handles() # can only call after submit and script template attributes are created.
        if not handles:#TODO need better serialization of handles # move handles logic elsewhere
            handles = self.create_handles()
        self.handles = Template(serializers['eq'](handles), # maybe just pass key_args ...
                                key_args=('label', 'project_dir', 'output_dir', 'output_path', 'socket_name'))

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

    def update_template(self, job_template:str, **kwargs): # same as update_templates, but without the protected args check
        self.templates.__getattribute__(job_template).update(**kwargs)
        """
        for name, template in zip(self.templates._fields, self.templates):
            if name == job_template:
                self.templates._replace( **{name: template.update(**kwargs)} )
        self.key_args = self.key_args | kwargs
        """
    def update_templates(self, **kwargs): # called from submit --
        #kwargs = serialize(kwargs, var = 'env', serializer = 'sh')
        if self.protected_args & kwargs.keys():
            raise KeyError("Protected args {} cannot be updated through Submit.update_templates(), only formatted".format(self.protected_args & kwargs.keys()))
        for template in self.templates:
            template.update(**kwargs)
        self.key_args = self.key_args | kwargs

    def __repr__(self):
        mkey_args = {key: self.key_args[key] for key in self.key_args if key not in self.protected_args}
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

submit args:
{}

protected args:
{}
""".format(*ssph, mkey_args, self.protected_args)

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
                flush_fptr(fptr)
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

_DEFAULT_SUBMIT = Template(template="sh {output_dir}/{label}.sh",
                           key_args={'output_dir', 'label'})

_DEFAULT_SCRIPT = Template(
    template= \
"""\
#!/bin/sh
cd {project_dir}

{handles}

export JOBID=$$

{env}
nohup {command} > {stdout} 2>&1 &
pid=$!
echo $pid >&1
""",
    key_args={'label', 'project_dir', 'output_dir', 'socket_name', 'stdout', 'stderr', 'env', 'command', 'handles'}
)

_DEFAULT_PATH = Template(template="{output_path}.sh",
                         key_args={'output_dir', 'label', 'output_path'})
_DEFAULT_HANDLES = runtk.ALL_HANDLES

_DEFAULT_KEY_ARGS = ('label', 'project_dir', 'output_dir', 'output_path', 'env', 'handles', 'socket_name', 'command', 'stdout', 'stderr', 'path')
class SHSubmit(Submit):
    # class attributes -- can be overridden in the calling __init__
    # or can be used via type( )

    SUBMIT_TEMPLATE  = _DEFAULT_SUBMIT
    SCRIPT_TEMPLATE  = _DEFAULT_SCRIPT
    PATH_TEMPLATE    = _DEFAULT_PATH
    HANDLES          = _DEFAULT_HANDLES
    KEY_ARGS         = _DEFAULT_KEY_ARGS

    def __init__(self,
                 submit_template = None,
                 script_template = None,
                 handles = None,
                 key_args = None,
                 **kwargs):
        #check for class attributes first, then passed arguments, then default values
        submit_template = submit_template or self.__class__.SUBMIT_TEMPLATE
        script_template = script_template or self.__class__.SCRIPT_TEMPLATE
        handles = handles or self.__class__.HANDLES
        key_args = key_args or self.__class__.KEY_ARGS
        super().__init__(
            submit_template = submit_template,
            script_template = script_template,
            handles = handles,
            key_args = key_args,
            **kwargs
        )

    def set_handles(self):
        pass

    def _parse_proc(self, proc) -> str:
        """
        [PROTECTED INTERNAL METHOD]
        SHSubmit.submit_job() calls this after Submit.submit_job()
        This internal method
        takes the proc returned by submitting job:
        (for instance the results of the shell call or through job scheduler)
        and returns a job_id.

        any logic (i.e. parsing proc in order to tell if the job submission succeeded or failed, and raising Error)
        should also be implemented here
        """
        return proc

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        self.job_id = self._parse_proc(proc)
        return self.job_id

# reference classes used as examples and for testing.
#TODO implement an option to autocomplete MSGFILE, SGLFILE, SOCNAME, JOBID... in submit_exports ...?
class SHSubmitSFS(SHSubmit):
    #KEY_ARGS = {'label', 'handles', 'project_dir', 'output_dir', 'env', 'command', 'stdout', 'stderr', 'path'}
    SCRIPT_TEMPLATE = \
        """\
#!/bin/sh
cd {project_dir}

{handles}

{env}
nohup {command} > {stdout} 2>&1 &
pid=$!
echo $pid >&1
"""
    HANDLES = runtk.ALL_HANDLES

class SHSubmitSOCK(SHSubmit):
    #KEY_ARGS = {'label', 'handles', 'project_dir', 'output_dir', 'env', 'command', 'stdout', 'stderr', 'path'}
    SCRIPT_TEMPLATE = \
        """\
#!/bin/sh
cd {project_dir}

{handles}

{env}
nohup {command} > {stdout} 2>&1 &
pid=$!
echo $pid >&1
"""
    HANDLES = runtk.ALL_HANDLES
