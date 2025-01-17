from batchtk.runtk.submits import Submit, FILE_HANDLES, Template

script_template = \
    """\
#!/bin/bash
#$ -N job{label}
#$ -q cpu.q
#$ -pe smp 1
#$ -l h_vmem=4G
#$ -l h_rt=00:30:00
#$ -o {output_path}/{label}.run
cd {project_path}
export OUTFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"
export JOBID=$JOBID
touch $OUTFILE
echo "hello world" > $OUTFILE
echo $JOBID > $OUTFILE
touch $SGLFILE
"""
submit_template = Template(template="source ~/.bash_profile;source ~/.bashrc;/ddn/age/bin/lx-amd64/qsub {output_path}/{label}.sh",
                           key_args={'output_path', 'label'})
script_template = Template(template=script_template,
                           key_args={'label', 'project_path', 'output_path', 'env', 'command'})
class SSHSubmitSFS(Submit):
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = submit_template,
            script_template = script_template,
            handles = FILE_HANDLES,
        )
    def submit_job(self, connection, **kwargs):
        super().submit_job(connection, **kwargs)
        return connection.run('qstat')