"""
test_job.py
this file runs a simple test between a dispatcher<->runner pair
it does not start a subprocess but validates that the file is appropriate and the runner has imported the correct values
to start bidirectional communication
the created environment. for subprocess testing, use test_zsh.py.
"""

import pytest
import os
from batchtk import runtk
from batchtk.runtk.dispatchers import INETDispatcher, UNIXDispatcher
from batchtk.runtk.submits import ZSHSubmitSOCK
from batchtk.runtk.runners import SocketRunner
from batchtk.utils import get_exports#TODO implement a more universal get_port_info
import logging
import json
from collections import namedtuple


Job = namedtuple('Job', ['Dispatcher', 'Submit'])
JOBS = [
        Job(INETDispatcher, ZSHSubmitSOCK),
        Job(UNIXDispatcher, ZSHSubmitSOCK)
        ]

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('test_job.log')

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)


class TestJOBS:
    @pytest.fixture(params=JOBS)
    def setup(self, request):
        Submit = request.param.Submit
        Dispatcher = request.param.Dispatcher
        dispatcher = Dispatcher(project_path=os.getcwd(),
                                     submit=Submit(),
                                     gid='test' + Dispatcher.__name__ + Submit.__name__)
        dispatcher.update_env({'strvalue': '1',
                               'intvalue': 2,
                               'fltvalue': 3.0})
        dispatcher.submit.update_templates(command='python test.py')
        return dispatcher

    def test_job(self, setup):
        dispatcher = setup
        dispatcher.create_job()
        assert os.path.exists(dispatcher.handles[runtk.SUBMIT])
        logger.info("dispatcher.env:\n{}".format(json.dumps(dispatcher.env)))
        logger.info("dispatcher.socket.name:\n{}".format(dispatcher.socket.name))
        logger.info("dispatcher.handles[runtk.SUBMIT]:\n{}".format(dispatcher.handles[runtk.SUBMIT]))
        #print(dispatcher.shellfile)
        with open(dispatcher.handles[runtk.SUBMIT], 'r') as fptr:
            script = fptr.read()
        logger.info("script:\n{}".format(script))
        #logger.info("port info (dispatcher listen):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        assert 'python test.py' in script
        env = get_exports(dispatcher.handles[runtk.SUBMIT])

        logger.info(env)
        runner = SocketRunner(env=env)
        logger.info("runner.socketname:\n{}".format(runner.socketname))
        runner.connect()
        connection, peer_address = dispatcher.accept()
        #logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        logger.info("runner.host_socket:\n{}".format(runner.host_socket))
        test_message = 'runner -> dispatcher message'
        runner.send(test_message)
        recv_message = dispatcher.recv()
        assert test_message == recv_message
        logger.info("""\
runner -> dispatcher message:
runner sent                  ---> dispatcher recv
{} ---> {}""".format(test_message, recv_message))
        test_message = 'dispatcher -> runner message'
        dispatcher.send(test_message)
        recv_message = runner.recv()
        logger.info("""\
dispatcher -> runner message:
dispatcher sent              ---> runner recv
{} ---> {}""".format(test_message, recv_message))
        assert test_message == recv_message
        runner.close()
        #logger.info("port info (runner close):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        dispatcher.clean()
        logger.info("runner.mappings:\n{}".format(json.dumps(runner.mappings)))
        assert runner.mappings['strvalue'] == '1'
        assert runner.mappings['intvalue'] == 2
        assert runner.mappings['fltvalue'] == 3.0
        #logger.info("port info (dispatcher clean):\n{}".format(get_port_info(dispatcher.socket.name[1])))
