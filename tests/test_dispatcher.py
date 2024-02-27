import pytest
import os

from pubtk.runtk.dispatchers import Dispatcher, SFS_Dispatcher, INET_Dispatcher

from pubtk.runtk.submits import Submit, SGESubmitSOCK, SGESubmitSFS, ZSHSubmitSOCK, ZSHSubmitSFS

class TestDispatcher:
    @pytest.fixture
    def setup(self):
        dispatcher = Dispatcher(env={'type': 'dispatcher'}, gid='dispatcher')
        return dispatcher

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.gid == 'dispatcher'
        assert dispatcher.env['type'] == 'dispatcher'

    def test_update_env(self, setup):
        dispatcher = setup
        dispatcher.add_dict({'new_var': 'new_value'}, value_type='STR')
        assert 'STRRUNTK1' in dispatcher.env
        assert dispatcher.env['STRRUNTK1'] == 'new_var=new_value'

class TestDispatcherSGESOCK:
    @pytest.fixture
    def setup(self):
        dispatcher = INET_Dispatcher(cwd=os.getcwd(),
                                     submit=SGESubmitSOCK(),
                                     env={'test': 'value'},
                                     gid='sgeinet')
        return dispatcher

    def test_add_command(self, setup):
        dispatcher = setup
        dispatcher.submit.update_templates(command='python test_runner.py')
        print(dispatcher.submit.script_template.template)
        assert "python test_runner.py" in dispatcher.submit.script_template.template

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == 'sgeinet'

    def test_add_dict(self, setup):
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
        dispatcher = INET_Dispatcher(cwd=os.getcwd(),
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

    def test_add_dict(self, setup):
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
        dispatcher = SFS_Dispatcher(cwd=os.getcwd(),
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
        print(dispatcher.submit)
        print(dispatcher.watchfile)
        print(dispatcher.readfile)
        print(dispatcher.shellfile)
        print(dispatcher.runfile)

class TestDispatcherSHSFS:
    @pytest.fixture
    def setup(self):
        dispatcher = SFS_Dispatcher(cwd=os.getcwd(),
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
        print(dispatcher.submit)
        print(dispatcher.watchfile)
        print(dispatcher.readfile)
        print(dispatcher.shellfile)
        print(dispatcher.runfile)