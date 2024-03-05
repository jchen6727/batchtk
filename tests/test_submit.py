import pytest
import os
from pubtk import runtk
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

class TestSubmit:
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