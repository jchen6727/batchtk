import pytest
import os
from collections import namedtuple
from batchtk.runtk.dispatchers import Dispatcher, INETDispatcher, UNIXDispatcher
from batchtk import runtk
from batchtk.runtk.submits import SHSubmit, SHSubmitSOCK, SHSubmitSFS

Job = namedtuple('Job', ['Dispatcher', 'Submit'])
JOBS = [
        Job(INETDispatcher, SHSubmitSOCK),
        Job(UNIXDispatcher, SHSubmitSOCK)
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
                                              label='test' + Dispatcher.__name__ + Submit.__name__)
        return namedtuple('Setup', ['dispatcher', 'submit'])(dispatcher, submit)

    def test_init(self, setup):
        dispatcher = setup.dispatcher
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.label == 'test' + type(dispatcher).__name__ + type(setup.submit).__name__

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
