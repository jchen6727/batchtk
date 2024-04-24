import pytest
import os
from collections import namedtuple
from batchtk.runtk.dispatchers import Dispatcher, INETDispatcher, UNIXDispatcher
from batchtk import runtk
from batchtk.runtk.submits import ZSHSubmit, ZSHSubmitSOCK, ZSHSubmitSFS

class TestDispatcher:
    @pytest.fixture
    def setup(self):
        dispatcher = Dispatcher(env={'type': 'base'}, gid='dispatcher_base')
        return dispatcher

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.gid == 'dispatcher_base'
        assert dispatcher.env['type'] == 'base'

    def test_update_env(self, setup):
        dispatcher = setup
        dispatcher.update_env({'new_var': 'new_value'}, value_type='STR')
        assert 'new_var=new_value' in dispatcher.env.values()

Job = namedtuple('Job', ['Dispatcher', 'Submit'])
JOBS = [
        Job(INETDispatcher, ZSHSubmitSOCK),
        Job(UNIXDispatcher, ZSHSubmitSOCK)
        ]

class TestJOBS:
    @pytest.fixture(params=JOBS)
    def setup(self, request):
        Submit = request.param.Submit
        submit = Submit()
        Dispatcher = request.param.Dispatcher
        dispatcher = Dispatcher(project_path=os.getcwd(),
                                              submit=submit,
                                              env={'test': 'value'},
                                              gid='test' + Dispatcher.__name__ + Submit.__name__)
        return namedtuple('Setup', ['dispatcher', 'submit'])(dispatcher, submit)

    def test_init(self, setup):
        dispatcher = setup.dispatcher
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == 'test' + type(dispatcher).__name__ + type(setup.submit).__name__

    def test_add_command(self, setup):
        dispatcher, submit = setup
        dispatcher.submit.update_templates(command='python test_runner.py')
        print(dispatcher.submit.script_template.template)
        assert "python test_runner.py" in dispatcher.submit.script_template.template


    def test_update_env(self, setup):
        dispatcher = setup.dispatcher
        dispatcher.update_env({'new_var': 'new_value'}, value_type='STR')
        assert 'new_var=new_value' in dispatcher.env.values()

    def test_create_job(self, setup):
        dispatcher = setup.dispatcher
        dispatcher.create_job()
        assert os.path.exists(dispatcher.handles[runtk.SUBMIT])
        with open(dispatcher.handles[runtk.SUBMIT], 'r') as fptr:
            script = fptr.read()
            print(script)
        for handle in set(dispatcher.handles).difference([runtk.SUBMIT]):
            assert dispatcher.handles[handle] in script
        dispatcher.clean()
        #assert os.path.exists(dispatcher.shellfile)
        #with open(dispatcher.shellfile, 'r') as fptr:
        #    script = fptr.read()
        #    print(script)
        #dispatcher.clean([])
