### Templates for SGE ###

class Submit(object):
    script_tmpl = ''
    submit_tmpl = ''
    def __init__(submit_tmpl, script_tmpl):
        self.script_tmpl = script_tmpl
        self.submit_tmpl = submit_tmpl
    def create(self, **kwargs):
        self.script_tmpl.format(**kwargs)
        self.submit_tmpl.format(**kwargs)
        return {'submit': self.submit_tmpl, 'script': script_str}

class SGE(object):
    
sge_template = \
"""\
#!/bin/bash
#$ -N {label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}{label}.run
cd {cwd}
source ~/.bashrc
export OUTFILE="{label}.out"
export SGLFILE="{label}.sgl"
{env}
{pre}{command}{post}
"""

### basic export environment
sh_template = \
"""\
#!/bin/sh
{header}
{env}
{command}
{footer}
"""