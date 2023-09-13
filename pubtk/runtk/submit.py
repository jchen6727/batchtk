### Submit class ###
import subprocess


def create_env(env):
    envstr = '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in env.items()])
    return envstr

class Submit(object):
    key_args = {'{label}', '{cwd}', '{env}'}
    def __init__(self, submit_template = str(), script_template = str()):
        self.submit_template = submit_template
        self.script_template = script_template
        self.job = dict()
        self.script_path = str()
        self.job_script = str()

    def format_job(self, **kwargs):
        submit = self.submit_template.format(**kwargs)
        script = self.script_template.format(**kwargs)
        self.job = {'submit': submit, 'script': script}
        self.script_path = "{cwd}/{label}".format(**kwargs)
        self.label = kwargs['label']
        return self.job

    def create_job(self, **kwargs):
        self.format_job(**kwargs)
        self.job_script = "{}.sh".format(self.script_path)
        fptr = open(self.job_script, 'w')
        fptr.write(self.job['script'])
        fptr.close()

    def submit_job(self):
        subprocess.Popen(self.job['submit'].split(), )
        self.proc = subprocess.run(self.job['submit'].split(' '), text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        return 1

    def __format__(self, **kwargs):
        return self.script_template.format(**kwargs)

    def format(self, **kwargs):
        return self.__format__(**kwargs)

class SGESubmit(Submit):
    Submit.key_args.update({'{command}', '{cores}', '{vmem}'})
    sge_template = \
        """\
        #!/bin/bash
        #$ -N {label}
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
    def __init__(self):
        super().__init__(submit_template = "qsub {label}.sh", script_template = self.sge_template)

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


