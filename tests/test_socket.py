import pytest
import logging
from batchtk.runtk.sockets import INETSocket
from header import LOG_PATH
logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_PATH(__file__))

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TestSocket:
    @pytest.fixture
    def socket_setup(self):
        return INETSocket(), INETSocket()

    def test_sockets(self, socket_setup):
        sock0, sock1 = socket_setup
        sock0.listen()
        sock1.connect(sock0.name)
        sock0.accept()
        sock0.send("hello")
        assert sock1.recv() == "hello"
        sock0.close()
        sock1.close()
