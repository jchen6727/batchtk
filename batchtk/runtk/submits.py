"""
batchtk.runtk.submits

This module provides the classes and functions responsible for generating,
formatting, and submitting job scripts in the batchtk framework. It acts as
the bridge between the Dispatcher and the execution environment by creating
executable scripts from templates and serializing environment variables.

Classes:
    Template: A wrapper around string templates that manages placeholders
        (key_args) and provides safe formatting and updating capabilities.
    Submit: The base class for defining a job submission. It manages the
        command, script, path, and handle templates, serializes environment
        variables, and provides methods to create and submit jobs.
    SHSubmit: A subclass of Submit configured with default templates for
        standard shell script (.sh) execution.
    SHSubmitSFS / SHSubmitSOCK: Example subclasses for specific configurations.

Functions:
    _check_submit_key_args: Helper function to validate template placeholders.
    serialize: Serializes environment variables into a specified format.

Usage:
    Submit objects are typically created by a Dispatcher to generate a job
    script. The Dispatcher calls `create_job()` to format the templates with
    the necessary environment variables and paths, and then `submit_job()`
    to write the script to disk and execute it via the configured protocol.
"""
import logging
from collections import namedtuple
from batchtk import runtk
from batchtk.utils import flush_fptr
import re
import warnings
import traceback
from batchtk.utils.version import deprecated_arg, deprecated_attribute, deprecated_class_attribute
#TODO, encapsulate file system #DONE, encapsulate connection #DONE


def _check_submit_key_args(submit_constructor):
    """
    Helper function--
    perform the default formatting method calls

    submit_constructor:

    simple_run:
    """
    #TODO -> move/consolidate this to utils.parser._check?
    submit = submit_constructor()

    templates = {
        'command': submit.templates.command,
        'script': submit.templates.script,
        'path': submit.templates.path,
    }

    missing_placeholders = {
        'command': [],
        'script': [],
        'path': [],
    }
    msg = (
        "submit attribute template {} missing {} placeholder...\n"
        "this can cause errors during execution...\n"
    )

    actual_keys = {}

    provided_keys = {}

    # check key args of each template before macro formatting:
    for label, template in templates.items:
        provided_keys[label] = template.key_args
        actual_keys[label] = set(template.get_args())


    # ensure that templates can format macro placeholders (will change template string)
    submit.update_template('command', output_path=runtk.OUTPUT_PATH_STR)
    submit.update_template('script', stdout=runtk.STDOUT_STR, stderr=runtk.STDERR_STR,
                                     output_path=runtk.OUTPUT_PATH_STR)
    submit.update_template('path'  , output_path=runtk.OUTPUT_PATH_STR)

    # update actual_keys of each template after doing macro formatting::
    for label, template in [submit.templates.command, submit.templates.script, submit.templates.path]:
        actual_keys[template] = actual_keys[template] | set(template.get_args())


    # check that there are relevant placeholders
    #TODO just check within the actual keys instead?
    rec = "recommend adding it (can use {output_path} for {output_dir}/{label})\n"
    # submit command should include {output_dir}/{label}
    for _str in ['{output_dir}', '{label}']:
        if _str not in submit.templates.command:
            missing_placeholders['command'].append(msg.format('command', _str))
    # submit script should include a cd {project_dir}
    for _str in ['{project_dir}', '{handles}', '{env}']:
        if _str not in submit.templates.script:
            missing_placeholders['script'].append(msg.format('command', _str))
    # submit path should include {output_dir}/{label}
    for _str in ['{output_dir}', '{label}']:
        if _str not in submit.templates.path:
            missing_placeholders['path'].append(msg.format('path', _str))

    # print statements
    for template in missing_placeholders:
        if missing_placeholders[template]:
            print(f'evaluation of {template} shows the following issues')
            for error in missing_placeholders[template]:
                print(error)
        else:
            print(f'evaluation of {template} passed successfully')

    for template in templates:
        if provided_keys != actual_keys:
            print(f"submit template attribute {template} has mismatched key args:\n"
                  f"provided: {provided_keys[template]}\n"
                  f"actual: {actual_keys[template]}")
        else:
            print(f"submit template attribute {template} has correct key args")

    return



class Template(object):
    """
    A wrapper class for string templates that provides safe formatting and updating.
    
    This class manages template placeholders (key_args) to prevent formatting errors
    when partial formatting is required. It allows placeholders to persist if they
    are not provided during formatting.
    
    Methods:
        __init__: Initializes the template and its key arguments.
        get_args: Extracts all placeholder names from the template string, called internally.
        format: Safely formats the template without modifying the original.
        update: Permanently updates the template by replacing provided placeholders.
        check_missing: Checks if any required placeholders remain unformatted.
    """
    def __new__(cls, template = None, key_args = None, **kwargs):
        if isinstance(template, Template):
            return template # any template object can be passed through -> see __init__
        else:
            return super().__new__(cls)

    def __init__(self, template, key_args = None, **kwargs): # ensure idempotency with the first check
        """
        Initializes the Template object. If another Template object is passed,
        it bypasses initialization.
        
        Args:
            template (str or Template): The template string with placeholders (e.g., "{key}").
            key_args (iterable, optional): An explicit list of allowed placeholders.
                If not provided, it automatically extracts them from the template string.
            
        Example:
            t = Template("echo {msg} to {file}", key_args=['msg', 'file'])
        """
        if isinstance(template, Template): # passthrough if already a Template
            return # why is this necessary?
        # if a template is passed to __new__, it returns an instance of Template, therefore calling the __init__ function
        self.template = template
        if key_args:
            self.key_args = {key: "{" + key + "}" for key in key_args}
        else:
            self.key_args = {key: "{" + key + "}" for key in self.get_args()}

    def get_args(self, **kwargs):
        """
        Extracts all format placeholders from the current template string using regex.
        
        Returns:
            list: A list of string placeholder names found in the template.
            
        Example:
            t = Template("command {arg1} {arg2}")
            t.get_args() # Returns ['arg1', 'arg2']
        """
        return re.findall(r'{(.*?)}', self.template)

#    def __format__(self, **kwargs):
#        mkwargs = self.key_args | kwargs
#        return self.template.format(mkwargs)

    def format(self, **kwargs):
        """
        Formats the template with the supplied kwargs, returning the formatted string.
        The template itself remains unchanged. Unspecified kwargs will remain as
        placeholders in the returned string.
        
        Args:
            **kwargs: Key-value pairs matching the template placeholders.
            
        Returns:
            str: The formatted template string.
            
        Example:
            t = Template("echo {a} {b}")
            t.format(a="hello") # Returns "echo hello {b}"
        """
        mkwargs = self.key_args | kwargs
        try:
            return self.template.format(**mkwargs)
        except KeyError as e:
            _new_key_args = {key: "{" + key + "}" for key in self.get_args()}
            message = (
                f"Warning:"
                f"for Template:\n{self}"
                f"In Template.format({kwargs}): argument '{e.args[0]}' was found in the script:"
                f"{self.template}"
                f"Recommend user provide '{e.args[0]}' to Template.key_args or in kwargs."
                f"current self.key_args:\n{self.key_args}"
                f"suggested self.key_args:\n{_new_key_args}"
                f"see traceback:\n{''.join(traceback.format_stack(limit=5))}" # avoid recursion?
            )
            warnings.warn(message)
            self.key_args = {key: "{" + key + "}" for key in self.get_args()}
            mkwargs = self.key_args | kwargs
            return self.template.format(**mkwargs)

    def update(self, **kwargs):
        """
        Permanently updates the template string in place by formatting it with
        the supplied kwargs. This function will preserve unspecified placeholders.
        
        Args:
            **kwargs: Key-value pairs to replace in the template.
            
        Example:
            t = Template("echo {msg} to {file}")
            t.update(msg="hello")
            print(t) # Output: "echo hello to {file}"
        """
        self.template = self.format(**kwargs)

    def check_missing(self, template):
        """
        Checks for missing keys (unformatted placeholders) in a provided template string.
        Typically used to validate that a formatting operation completed successfully.
        
        Args:
            template (str): The formatted string to check.
            
        Returns:
            list: A list of keys that are still present as placeholders in the string.
            
        Example:
            t = Template("echo {a} {b}")
            formatted_str = t.format(a="1")
            t.check_missing(formatted_str) # Returns ['b']
        """
        return [key for key in self.key_args if key in template]


    def __repr__(self):
        """
        Returns the raw template string.
        """
        return self.template

    def __call__(self, **kwargs):
        """
        Allows calling the Template instance directly to format it.
        Alias for format().
        """
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


_Job = namedtuple('job', 'command script path handles')

@deprecated_attribute('submit', 'command', deprecated_since='0.1.0')
@deprecated_attribute('submit_template', 'command_template', deprecated_since='0.1.0')
class Submit(object):
    @deprecated_arg({'submit_template': 'command_template'}, deprecated_since='0.1.0')
    def __init__(self, command_template, script_template, path_template=None, handles=None, log=None,
                 key_args=('label', 'project_dir', 'output_dir', 'output_path', 'env', 'handles', 'socket_name', 'command', 'stdout', 'stderr', 'path'),
                 protected_args=('label', 'project_dir', 'output_dir', 'output_path', 'env', 'handles', 'socket_name', 'stdout', 'stderr', 'path'),
                 **kwargs):

        #key_args can be updated and formatted,
        #protected_args can only be formatted
        self.command_template = Template(command_template, key_args=key_args)
        self.script_template = Template(script_template, key_args=key_args)
        self.path_template = path_template or Template(self.command_template.template.split(' ')[-1])
        self.key_args = self.command_template.key_args | self.script_template.key_args | self.path_template.key_args
        self.protected_args = set(protected_args)
        handles = handles or self.create_handles() # can only call after submit and script template attributes are created.
        if not handles:#TODO need better serialization of handles # move handles logic elsewhere
            handles = self.create_handles()
        self.handles = Template(serializers['eq'](handles), # maybe just pass key_args ...
                                key_args=('label', 'project_dir', 'output_dir', 'output_path', 'socket_name'))

        self.templates = _Job(self.command_template, self.script_template, self.path_template, self.handles)
        self.job = None
        self.command = None
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
        self.job     = job
        self.command = job.command
        self.script  = job.script
        self.path    = job.path
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
            csph = self.job._replace(handles=self.repr_handles()) #command, script, path, handles
        else:
            csph = self.templates._replace(handles=self.repr_handles())
        return """
command:
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
""".format(*csph, mkey_args, self.protected_args)

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
        self.proc = cmd.run(self.job.command)
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

_DEFAULT_COMMAND = Template(template="sh {output_dir}/{label}.sh",
                           key_args={'output_path', 'output_dir', 'label'})

_DEFAULT_SCRIPT = Template(
    template= \
"""\
#!/bin/sh

source ~/.bashrc

cd {project_dir}

{handles}
{env}

export JOBID=$$
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

@deprecated_class_attribute('SUBMIT_TEMPLATE', 'COMMAND_TEMPLATE', deprecated_since='0.1.0')
class SHSubmit(Submit):
    # class attributes -- can be overridden in the calling __init__
    # or can be used via type( )

    COMMAND_TEMPLATE = _DEFAULT_COMMAND
    SCRIPT_TEMPLATE  = _DEFAULT_SCRIPT
    PATH_TEMPLATE    = _DEFAULT_PATH
    HANDLES          = _DEFAULT_HANDLES
    KEY_ARGS         = _DEFAULT_KEY_ARGS

    @deprecated_arg({'submit_template': 'command_template'}, deprecated_since='0.1.0')
    def __init__(self,
                 command_template = None,
                 script_template = None,
                 path_template = None,
                 handles = None,
                 key_args = None,
                 **kwargs):
        #check for class attributes first, then passed arguments, then default values
        command_template = command_template or self.__class__.COMMAND_TEMPLATE
        script_template = script_template or self.__class__.SCRIPT_TEMPLATE
        path_template = path_template or self.__class__.PATH_TEMPLATE
        handles = handles or self.__class__.HANDLES
        key_args = key_args or self.__class__.KEY_ARGS
        super().__init__(
            command_template = command_template,
            script_template = script_template,
            path_template = path_template,
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
