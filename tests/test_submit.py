import pytest
import os
from batchtk import runtk
from batchtk.runtk.submits import Submit
from batchtk.utils import get_port_info
import logging
import json
from header import CLEAN_OUTPUTS, LOG_PATH

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_PATH(__file__))

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

script_template = """\
#!/bin/bash
cd {project_path}
export JOBID=$$
{env}
nohup {command} > /tmp/foo/{label}.run 2>&1 &
export OUTFILE="/tmp/foo/{label}.out"
export SGLFILE="/tmp/foo/{label}.sgl"
export SOCNAME="{sockname}"
"""
class TestSubmit:
    @pytest.fixture
    def submit_setup(self):
        submit = Submit(
            submit_template = "sh /tmp/foo/bar.sh",
            script_template = script_template,
        )
        yield submit

    def test_submit(self, submit_setup):
        submit = submit_setup
        handles = submit.get_handles()
        for handle in runtk.HANDLES:
            assert handle in handles.keys()
        logger.info("handles:\n{}".format(json.dumps(handles)))
        logger.info(submit)
        submit.create_job(project_path='/tmp/foo/', label='test', sockname='test.sock', env={'VAR0': 'VAL0', 'VAR1': 'VAL1'}, command='echo "hello world"')
        handles = submit.get_handles()
        logger.info("handles:\n{}".format(json.dumps(handles)))
        logger.info(submit)
