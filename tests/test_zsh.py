import pytest
import os
from pubtk.runtk.dispatchers import Dispatcher, INET_Dispatcher
from pubtk.runtk.submits import Submit, ZSHSubmitSOCK
from pubtk.utils import get_port_info
import logging
import json


logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('test_zsh.log')

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TestZSHINET:
    @pytest.fixture
    def dispatcher_setup(self):
        dispatcher = INET_Dispatcher(project_path=os.getcwd(),
                                     submit=ZSHSubmitSOCK(),
                                     gid='test_sh_shinet')
        dispatcher.update_env({'strvalue': '1',
                               'intvalue': 2,
                               'fltvalue': 3.0})
        dispatcher.submit.update_templates(command='python runner_scripts/socket_py.py')
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
        assert 'python runner_scripts/socket_py' in script
        dispatcher.submit_job()
        logger.info("job id:\n{}".format(dispatcher.job_id))
        connection, peer_address = dispatcher.accept()
        logger.info("""\
        connection:   {}
        peer_address: {}""".format(connection, peer_address))
        logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.socket.name[1])))

        dispatcher.send("hello")
        recv_message = dispatcher.recv()
        logger.info("mappings:\n{}".format(recv_message))

        recv_message = dispatcher.recv()
        logger.info("results:\n{}".format(recv_message))
        dispatcher.send("goodbye")
        logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        #logger.info("result:\n{}".format(recv_message))
        logger.info("port info (runner close):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        dispatcher.clean([])
        logger.info("port info (dispatcher close:\n{}".format(get_port_info(dispatcher.socket.name[1])))

if __name__ == '__main__':
    pytest.main(['-s', __file__])