# used in test_job, test_serialize and test_trial0.py

TEST_ENVIRONMENT = {
    'strvalue': '1',
    'intvalue': 2,
    'fltvalue': 3.0,
    'dictvalue': {'key': 'value'}, #TODO serialization needs to json.dumps properly
    'listvalue': [1, 2.0, "3, 4, 5"],
}

OUTPUT_PATH = lambda name: '{}/test_outputs/{}'.format(name.rsplit('/', 1)[0], name.rsplit('/', 1)[1].split('.', 1)[0])

LOG_PATH = lambda name: '{}/test_logs/{}.log'.format(name.rsplit('/', 1)[0], name.rsplit('/', 1)[1].split('.', 1)[0])

import re
import subprocess
import shlex
import os

def GET_EXPORTS(filename):
    with open(filename, 'r') as fptr:
        items = re.findall(r'export (.*?)="(.*?)"', fptr.read())
        return {key: val for key, val in items}

def GET_PORT_INFO(port):
    output = subprocess.run(shlex.split('lsof -i :{}'.format(port)), capture_output=True, text=True)
    if output.returncode == 0:
        return output.stdout
    else:
        return output.returncode

def CLEAN_OUTPUTS(dispatcher, runner=None):
    if dispatcher.handles is not None:
        print("cleanup, removing handles: \n{}".format('\n'.join(dispatcher.get_handles().values())))
        print("cleanup, removing output directory: \n{}".format(dispatcher.output_path))
        dispatcher.clean('all')
    os.rmdir(dispatcher.output_path)
    if runner is not None:
        runner.close()