import pytest
import os

from pubtk.runtk.dispatchers import Dispatcher, SFS_Dispatcher, INET_Dispatcher

from pubtk.runtk.submits import ZSHSubmit, ZSHSubmitSOCK, ZSHSubmitSFS

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

SUBMITS = [ZSHSubmit, ZSHSubmitSOCK, ZSHSubmitSFS]
class TestDispatcherZSHSubmit:
    @pytest.fixture(params=SUBMITS)
    def setup(self, request):
        submit = request.param()
        dispatcher = INET_Dispatcher(project_path=os.getcwd(),
                                     submit=submit,
                                     env={'test': 'value'},
                                     gid='sgeinet')
        return dispatcher, submit

    def test_add_command(self, setup):
        dispatcher = setup
        dispatcher.submit.update_templates(command='python test_runner.py')
        print(dispatcher.submit.script_template.template)
        assert "python test_runner.py" in dispatcher.submit.script_template.template

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == 'sgeinet'

    def test_update_env(self, setup):
        dispatcher = setup
        dispatcher.update_env({'new_var': 'new_value'}, value_type='STR')
        assert 'STRRUNTK1' in dispatcher.env
        assert dispatcher.env['STRRUNTK1'] == 'new_var=new_value'

    def test_create_job(self, setup):
        dispatcher = setup
        dispatcher.create_job()
        assert os.path.exists(dispatcher.shellfile)
        with open(dispatcher.shellfile, 'r') as fptr:
            script = fptr.read()
            print(script)
        dispatcher.clean([])

class TestDispatcherSHSOCK:
    @pytest.fixture
    def setup(self):
        dispatcher = INET_Dispatcher(project_path=os.getcwd(),
                                     submit=ZSHSubmitSOCK(),
                                     env={'test': 'value'},
                                     gid='shinet')
        return dispatcher

    def test_add_command(self, setup):
        dispatcher = setup
        dispatcher.submit.update_templates(command='python test_runner.py')
        print(dispatcher.submit.script_template.template)
        assert "python test_runner.py" in dispatcher.submit.script_template.template

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == 'shinet'

    def test_update_env(self, setup):
        dispatcher = setup
        dispatcher.update_env({'new_var': 'new_value'}, value_type='STR')
        assert 'STRRUNTK1' in dispatcher.env
        assert dispatcher.env['STRRUNTK1'] == 'new_var=new_value'

    def test_create_job(self, setup):
        dispatcher = setup
        dispatcher.create_job()
        assert os.path.exists(dispatcher.shellfile)
        with open(dispatcher.shellfile, 'r') as fptr:
            script = fptr.read()
            print(script)
        dispatcher.clean([])
class TestDispatcherSGESFS:
    @pytest.fixture
    def setup(self):
        dispatcher = SFS_Dispatcher(project_path=os.getcwd(),
                                    submit=SGESubmitSFS(),
                                    env={'test': 'value'},
                                    gid='123')
        return dispatcher

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == '123'

    def test_create_job(self, setup):
        dispatcher = setup
        dispatcher.create_job()
        print(dispatcher.handles)


class TestDispatcherSHSFS:
    @pytest.fixture
    def setup(self):
        dispatcher = SFS_Dispatcher(project_path=os.getcwd(),
                                    submit=ZSHSubmitSFS(),
                                    env={'test': 'value'},
                                    gid='123')
        return dispatcher

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == '123'

    def test_create_job(self, setup):
        dispatcher = setup
        dispatcher.create_job()
        print(dispatcher.handles)
