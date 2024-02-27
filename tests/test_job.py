import pytest
import os
from pubtk.runtk.dispatchers import Dispatcher, SFS_Dispatcher, INET_Dispatcher
from pubtk.runtk.submits import Submit, SGESubmitSOCK, SGESubmitSFS, ZSHSubmitSFS, ZSHSubmitSOCK
from pubtk.runtk.runners import SocketRunner
from pubtk.utils import get_exports, get_port_info
import logging
import json


logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('test_job.log')

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)
class TestSGEINET:
    @pytest.fixture
    def dispatcher_setup(self):
        dispatcher = INET_Dispatcher(cwd=os.getcwd(),
                                     submit=SGESubmitSOCK(),
                                     gid='test_job_sgeinet')
        dispatcher.update_env({'strvalue': '1',
                               'intvalue': 2,
                               'fltvalue': 3.0})
        dispatcher.submit.update_templates(command='python test.py',
                                           cores='8',
                                           vmem='32G')
        return dispatcher

    def test_job(self, dispatcher_setup):
        dispatcher = dispatcher_setup
        dispatcher.create_job()
        assert os.path.exists(dispatcher.shellfile)
        logger.info("dispatcher.env:\n{}".format(json.dumps(dispatcher.env)))
        logger.info("dispatcher.socket.name:\n{}".format(dispatcher.socket.name))
        logger.info("dispatcher.shellfile:\n{}".format(dispatcher.shellfile))
        #print(dispatcher.shellfile)
        with open(dispatcher.shellfile, 'r') as fptr:
            script = fptr.read()
            #print(script)
        logger.info("script:\n{}".format(script))
        logger.info("port info (dispatcher listen):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        assert 'python test.py' in script
        env = get_exports(dispatcher.shellfile)

        logger.info(env)
        runner = SocketRunner(env=env)
        logger.info("runner.socketname:\n{}".format(runner.socketname))
        runner.connect()
        connection, peer_address = dispatcher.accept()
        logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.socket.name[1])))
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
        logger.info("port info (runner close):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        dispatcher.clean()
        logger.info("runner.mappings:\n{}".format(json.dumps(runner.mappings)))
        assert runner.mappings['strvalue'] == '1'
        assert runner.mappings['intvalue'] == 2
        assert runner.mappings['fltvalue'] == 3.0
        logger.info("port info (dispatcher clean):\n{}".format(get_port_info(dispatcher.socket.name[1])))

class TestSHINET:
    @pytest.fixture
    def dispatcher_setup(self):
        dispatcher = INET_Dispatcher(cwd=os.getcwd(),
                                     submit=ZSHSubmitSOCK(),
                                     gid='test_job_shinet')
        dispatcher.update_env({'strvalue': '1',
                               'intvalue': 2,
                               'fltvalue': 3.0})
        dispatcher.submit.update_templates(command='python test.py')
        return dispatcher

    def test_job(self, dispatcher_setup):
        dispatcher = dispatcher_setup
        dispatcher.create_job()
        assert os.path.exists(dispatcher.shellfile)
        logger.info("dispatcher.env:\n{}".format(json.dumps(dispatcher.env)))
        logger.info("dispatcher.socket.name:\n{}".format(dispatcher.socket.name))
        logger.info("dispatcher.shellfile:\n{}".format(dispatcher.shellfile))
        #print(dispatcher.shellfile)
        with open(dispatcher.shellfile, 'r') as fptr:
            script = fptr.read()
            #print(script)
        logger.info("script:\n{}".format(script))
        logger.info("port info (dispatcher listen):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        assert 'python test.py' in script
        env = get_exports(dispatcher.shellfile)

        logger.info(env)
        runner = SocketRunner(env=env)
        logger.info("runner.socketname:\n{}".format(runner.socketname))
        runner.connect()
        connection, peer_address = dispatcher.accept()
        logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.socket.name[1])))
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
        logger.info("port info (runner close):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        dispatcher.clean()
        logger.info("runner.mappings:\n{}".format(json.dumps(runner.mappings)))
        assert runner.mappings['strvalue'] == '1'
        assert runner.mappings['intvalue'] == 2
        assert runner.mappings['fltvalue'] == 3.0
        logger.info("port info (dispatcher clean):\n{}".format(get_port_info(dispatcher.socket.name[1])))
