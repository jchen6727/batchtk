from batchtk.runtk.dispatchers import SHDispatcher
from fabric import Connection, Config
from paramiko.ssh_exception import SSHException
from batchtk.sshtk.utils import _deploy_project
from collections import namedtuple
from batchtk import runtk
from batchtk.utils import create_path, RemoteCmd, RemoteFS, BaseFS

class _Status(namedtuple('status', ['status', 'msg'])):
    def __repr__(self):
        return 'status={}, msg={}'.format(self.status, self.msg)


class SSHDispatcher(SHDispatcher):
    """
    SSH Dispatcher, for running jobs on remote machines
    uses fabric, paramiko
    """
    def __init__(self, submit=None, host=None, remote_dir=None, fs=None,
                 remote_out='.', connection=None, config_path='~/.ssh/config',
                 fabric_config=None, env=None, label=None, **kwargs):
        """
        Parameters
        ----------
        host - the ssh host
        cmdstr - the command to run on the remote machine
        env - any environmental variables to be inherited by the created runner
        """
        self.init_connections(connection=connection, host=host, config_path=config_path, fabric_config=fabric_config, fs=fs)
        super().__init__(submit=submit, project_path=remote_dir, output_path=remote_out, label=label, env=env,
                         fs=RemoteFS(host=host), cmd=RemoteCmd(self.connection), **kwargs)
        #self.fs = RemoteFS(host=host)
        #self.cmd = RemoteCmd(self.connection)
        #self.host = host
        #self.project_path = remote_dir
        #self.local_dir = local_dir
        self.output_path = create_path(remote_dir, remote_out, self.fs)
        #self.ssh_config = fabric_config or Config(user_ssh_path=config_path)
        #self.connection = Connection(host, config=self.ssh_config)
        self.handles = None
        self.job_id = -1
        #self._stuple = namedtuple('status', ['status', 'msg'])

    def init_connections(self, connection=None, host=None, config_path='~/.ssh/config', fabric_config=None, fs=None):
        self.init_args = locals()
        self.init_args.pop('self')
        self.connection = None
        self.fs = None
        if isinstance(connection, Connection):
            self.connection = connection
        if host and self.connection is None:
            config = fabric_config or Config(user_ssh_path=config_path)
            self.connection = Connection(host, config=config)
        if self.connection is None:
            raise ValueError('no SSH connection was established')
        if isinstance(fs, BaseFS):
            self.fs = fs
        if fs is None:
            self.fs = RemoteFS(host=host)
        if self.fs is None:
            raise ValueError('no file system was established')

    def open_connections(self):
        self.init_connections(**self.init_args)

    def close_connections(self):
        self.fs.close()
        self.connection.close()
        self.fs = None
        self.connection = None

    def reset_connections(self):
        self.close_connections()
        self.open_connections()

    def get_handles(self):
        if not self.handles:
            self.create_job()
        return self.handles

    def check_status(self):
        handles = self.get_handles()
        submit, msgout, sglout = handles[runtk.SUBMIT], handles[runtk.MSGOUT], handles[runtk.SGLOUT]
        if not self.fs.exists(submit):
            return _Status(runtk.STATUS.NOTFOUND, None)
        if not self.fs.exists(msgout):
            return _Status(runtk.STATUS.PENDING, None)
        msg = self.fs.tail(msgout)
        if self.fs.exists(sglout):
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
            proc = self.submit.submit_job(fs=self.fs, cmd=self.cmd)
            self.job_id = proc.stdout
            return self.check_status()
        return status
