from batchtk.runtk.dispatchers import SHDispatcher
from fabric import Connection, Config
from paramiko.ssh_exception import SSHException
from batchtk.sshtk.utils import _deploy_project
from collections import namedtuple
from batchtk import runtk
from batchtk.utils import create_path, RemoteCmd, RemoteFS

class _Status(namedtuple('status', ['status', 'msg'])):
    def __repr__(self):
        return 'status=({}):{}: msg={}'.format(self.status, runtk.STATUS_HANDLES[self.status], self.msg)


class SSHDispatcher(SHDispatcher):
    """
    SSH Dispatcher, for running jobs on remote machines
    uses fabric, paramiko
    """
    def __init__(self, submit=None, host=None, remote_dir=None, remote_out='.', local_dir='/tmp', connection=None, config_path='~/.ssh/config', fabric_config=None, env=None, gid=None, **kwargs):
        """
        Parameters
        ----------
        host - the ssh host
        cmdstr - the command to run on the remote machine
        env - any environmental variables to be inherited by the created runner
        """
        super().__init__(submit=submit, project_path=local_dir, output_path=local_dir, gid=gid, env=env, **kwargs)
        self.connection = None
        if connection and isinstance(connection, Connection):
            self.connection = connection
        if host and not self.connection:
            config = fabric_config or Config(user_ssh_path=config_path)
            self.connection = Connection(host, config=config)
        if not self.connection:
            raise ValueError('no connection was established')
        self.fs = RemoteFS(host=host)
        self.cmd = RemoteCmd(self.connection)
        self.host = host
        self.project_path = remote_dir
        self.local_dir = local_dir
        self.output_path = create_path(remote_dir, remote_out, RemoteFS())
        #self.ssh_config = fabric_config or Config(user_ssh_path=config_path)
        #self.connection = Connection(host, config=self.ssh_config)
        self.handles = None
        self.job_id = -1
        #self._stuple = namedtuple('status', ['status', 'msg'])

    def get_handles(self):
        if not self.handles:
            self.create_job()
        return self.handles

    def check_status(self):
        handles = self.get_handles()
        submit, msgout, sglout = handles[runtk.SUBMIT], handles[runtk.MSGOUT], handles[runtk.SGLOUT]
        if self.connection.run('[ -f {} ]'.format(submit), warn=True, hide=True).exited == 1:
            return _Status(runtk.STATUS.NOTFOUND, None)
        if self.connection.run('[ -f {} ]'.format(msgout), warn=True, hide=True).exited == 1:
            return _Status(runtk.STATUS.PENDING, None)
        msg = self.connection.run('tail -n1 {}'.format(msgout), warn=True, hide=True).stdout
        if self.connection.run('[ -f {} ]'.format(sglout), warn=True, hide=True).exited == 0:
            return _Status(runtk.STATUS.COMPLETED, msg)
        return _Status(runtk.STATUS.RUNNING, msg)

    def create_job(self, **kwargs):
        """
        creates a job through the submit instance
        the `label` is created, and the relevant commands and scripts are created,
        then the handles are retrieved from the submit instance

        :param kwargs: #TODO use this format in all docstrings :/
        :return:
        """
        super().init_run()
        self.submit.create_job(label=self.label,
                               project_path=self.project_path,
                               output_path=self.output_path,
                               env=self.env,
                               **kwargs)
        self.handles = self.submit.get_handles()


    def submit_job(self):
        status = self.check_status()
        if status.status in [runtk.STATUS.PENDING, runtk.STATUS.RUNNING, runtk.STATUS.COMPLETED]:
            return status
        if status.status is runtk.STATUS.NOTFOUND:
            tmp_file = "{}/{}.out".format(self.local_dir, self.label)
            with open(tmp_file, 'w') as fptr:
                fptr.write(self.submit.script)
            self.connection.run("mkdir -p {}".format(self.output_path))
            self.connection.put(tmp_file, self.handles[runtk.SUBMIT])
            #self.connection.run("echo '{}' > {}".format(self.submit.script, self.handles[runtk.SUBMIT]))
            proc = self.connection.run("{}".format(self.submit.submit), hide=True)
            self.job_id = proc.stdout
            return self.check_status()
        return status


