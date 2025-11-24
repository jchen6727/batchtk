from batchtk.runtk.dispatchers import SSHDispatcher
from batchtk.utils import TOTPConnection
from fabric import connection
from batchtk.runtk.submits import SHSubmitSFS


from fabric import connection

connection_kwargs = {'host': 'grid0'}
dispatcher = SSHDispatcher(
    connection_constructor = connection.Connection,
    connection_kwargs = connection_kwargs,
    submit = SHSubmitSFS,
    project_dir = '/ddn/jchen/dev',
    output_dir = '.',
    env = {},
    label = 'trial',
)
print('hello')
dispatcher.start()