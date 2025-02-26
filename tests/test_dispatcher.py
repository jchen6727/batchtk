import pytest
import os
from collections import namedtuple
from batchtk.runtk.dispatchers import Dispatcher, LocalDispatcher, QSDispatcher
from batchtk import runtk
from batchtk.runtk.submits import SHSubmitSFS
import uuid
from header import OUTPUT_PATH, CLEAN_OUTPUTS


Job = namedtuple('Job', ['Dispatcher', 'Submit'])
JOBS = [
        Job(LocalDispatcher, SHSubmitSFS),
        ]

class TestJOBS:
    @pytest.fixture(params=JOBS)
    def setup(self, request):
        _Submit = request.param.Submit
        submit = _Submit()
        _Dispatcher = request.param.Dispatcher
        uid = str(uuid.uuid4())
        key_uid = 'j_'+uid[:4]
        env = {key_uid: uid}
        dispatcher = _Dispatcher(project_path=__file__.rsplit('/', 1)[0],
                                 output_path=OUTPUT_PATH(__file__),
                                              submit=submit,
                                              env=env,
                                              label='test' + _Dispatcher.__name__ + _Submit.__name__)
        yield namedtuple('Setup', ['dispatcher', 'submit', 'env'])(dispatcher, submit, env)
        CLEAN_OUTPUTS(dispatcher)

    def test_init(self, setup):
        dispatcher, env = setup.dispatcher, setup.env
        for key in env:
            assert env[key] == dispatcher.env[key]
        assert dispatcher.label == 'test' + type(dispatcher).__name__ + type(setup.submit).__name__

    def test_add_command(self, setup):
        dispatcher, submit, env = setup
        dispatcher.submit.update_templates(command='python test_runner.py')
        print(dispatcher.submit.script_template.template)
        assert "python test_runner.py" in dispatcher.submit.script_template.template


    def test_update_env(self, setup):
        dispatcher = setup.dispatcher
        dispatcher.update_env({'new_var': 'new_value'}, value_type='STR')
        assert 'new_var{}new_value'.format(runtk.EQDELIM) in dispatcher.env.values()

    def test_create_job(self, setup):
        dispatcher = setup.dispatcher
        dispatcher.create_job()
        assert dispatcher.handles is not None
        print(dispatcher.handles)

    def test_create_and_submit(self, setup):
        dispatcher, env = setup.dispatcher, setup.env
        env = [*env.items()][0]
        dispatcher.submit.update_templates(command='printenv | grep {} | tee -a "$MSGFILE" "$SGLFILE"'.format(env[0]))
        if isinstance(dispatcher, QSDispatcher):
            status = dispatcher.check_status()
            print("\nprior to job submission: {}\n".format(status))
            assert status.status == runtk.STATUS.NOTFOUND
        dispatcher.create_job()
        dispatcher.submit_job()
        with open(dispatcher.handles[runtk.SUBMIT], 'r') as fptr:
            script = fptr.read()
            print(script)
        for handle in set(dispatcher.handles).difference([runtk.SUBMIT]):
            assert dispatcher.handles[handle] in script
        for handle in set(dispatcher.handles).difference([runtk.SOCKET]):
            assert dispatcher.fs.exists(dispatcher.handles[handle])
        data = dispatcher.recv(interval=15)
        assert env[0] in data
        assert env[1] in data
        if isinstance(dispatcher, QSDispatcher):
            status = dispatcher.check_status()
            print("\nafter to job submission: {}\n".format(status))
            assert status.status == runtk.STATUS.COMPLETED
        dispatcher.clean('all')
        for handle in set(dispatcher.handles).difference([runtk.SOCKET]):
            assert not dispatcher.fs.exists(dispatcher.handles[handle])


        #dispatcher.clean('all')
        #for handle in set(dispatcher.handles).difference([runtk.SUBMIT]):
        #    assert not dispatcher.fs.exists(dispatcher.handles[handle])
        #assert os.path.exists(dispatcher.shellfile)
        #with open(dispatcher.shellfile, 'r') as fptr:
        #    script = fptr.read()
        #    print(script)
        #dispatcher.clean([])
