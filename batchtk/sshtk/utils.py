from fabric import Connection, Config
from fabric.transfer import Transfer
from paramiko.ssh_exception import SSHException
from shutil import make_archive
import os
from batchtk.runtk import STATUS

def _deploy_project(connection, project_dir=None, remote_dir=None, label=None, deploy_command=None, **kwargs ):
    if not project_dir:
        raise ValueError('no local project directory (project_dir) was supplied')
    if not remote_dir:
        raise ValueError('no remote directory (remote_dir) was supplied')
    if not label:
        raise ValueError('no label (label) was supplied')
    make_archive('{}'.format(label), 'tar', project_dir)
    if connection.run('[ -d {}/{} ]'.format(remote_dir, label), warn=True) == 0:
        return (STATUS.EXISTS, connection)
    connection.put('{}.tar'.format(label), remote_dir, label)
    os.remove('{}.tar'.format(label))
    connection.run('mkdir -p {}/{}'.format(remote_dir, label))
    connection.run('tar -xvf {}/{}.tar -C {}/{}'.format(remote_dir, label, remote_dir, label))
    if deploy_command:
        connection.run('cd {}/{}; {}'.format(remote_dir, label, deploy_command))
    return (STATUS.SUCCESS, connection)

def deploy_project(config=None, config_path=None, connection=None, host=None, **kwargs):
    if config and not isinstance(config, Config):
        return ValueError('supplied config must be an instance of fabric.Config')
    if config_path:
        config = Config(user_ssh_path=config_path)
    if connection and not isinstance(connection, Connection):
        return ValueError('supplied connection must be an instance of fabric.Connection')
    if config and host:
        connection = Connection(host=host, config=config)
    if not connection:
        return ValueError('no connection was established')
    return _deploy_project(connection, **kwargs)


"""
Your job 164890 ("jobnew_project") has been submitted

"""



