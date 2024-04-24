import pytest
import os
from batchtk import runtk
from batchtk.runtk.dispatchers import INETDispatcher, UNIXDispatcher
from batchtk.runtk.submits import SHSubmitSOCK
#from batchtk.utils import get_port_info #TODO implement a more universal get_port_info
import logging
import json
from collections import namedtuple

Job = namedtuple('Job', ['Dispatcher', 'Submit'])
JOBS = [
        Job(INETDispatcher, SHSubmitSOCK),
        Job(UNIXDispatcher, SHSubmitSOCK)
        ]

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('test_sh.log')

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TestSHINET:
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
        dispatcher.submit.update_templates(command='python runner_scripts/socket_py.py')
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
            #print(script)
        logger.info("script:\n{}".format(script))
        #logger.info("port info (dispatcher listen):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        assert 'python runner_scripts/socket_py' in script
        dispatcher.submit_job()
        logger.info("job id:\n{}".format(dispatcher.job_id))
        connection, peer_address = dispatcher.accept()
        logger.info("""\
        connection:   {}
        peer_address: {}""".format(connection, peer_address))
        #logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.socket.name[1])))

        dispatcher.send("hello")
        recv_message = dispatcher.recv()
        logger.info("mappings:\n{}".format(recv_message))

        recv_message = dispatcher.recv()
        logger.info("results:\n{}".format(recv_message))
        dispatcher.send("goodbye")
        #logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        #logger.info("result:\n{}".format(recv_message))
        #logger.info("port info (runner close):\n{}".format(get_port_info(dispatcher.socket.name[1])))
        dispatcher.clean()
        #logger.info("port info (dispatcher close:\n{}".format(get_port_info(dispatcher.socket.name[1])))

if __name__ == '__main__':
    pytest.main(['-s', __file__])