import pytest
import os
from pubtk.runtk.dispatchers import Dispatcher, SFS_Dispatcher, INET_Dispatcher
from pubtk.runtk.submit import Submit, SGESubmitINET, SGESubmitSFS

class TestDispatcher:
    @pytest.fixture
    def setup(self):
        dispatcher = Dispatcher(env={'test': 'value'}, gid='123')
        return dispatcher

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == '123'

    def test_add_dict(self, setup):
        dispatcher = setup
        dispatcher.add_dict({'new_var': 'new_value'}, value_type='str')
        assert 'strRUNTK1' in dispatcher.env
        assert dispatcher.env['strRUNTK1'] == 'new_var=new_value'

    def test_add_val(self, setup):
        dispatcher = setup
        dispatcher.add_val('str', 'new_var', 'new_value')
        assert 'strRUNTK1' in dispatcher.env
        assert dispatcher.env['strRUNTK1'] == 'new_var=new_value'


class TestDispatcherSGEINET:
    @pytest.fixture
    def setup(self):
        dispatcher = INET_Dispatcher(cwd=os.getcwd(),
                                     submit=SGESubmitINET(),
                                     env={'test': 'value'},
                                     gid='123')
        return dispatcher

    def test_add_command(self, setup):
        print()
        dispatcher = setup
        dispatcher.submit.update_job(command='python test_runner.py')
        print(dispatcher.submit.script_template.get_args())
        print(dispatcher.submit)
        assert "python test_runner.py" in dispatcher.submit.job.script

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.gid == '123'

    def test_add_dict(self, setup):
        dispatcher = setup
        dispatcher.add_dict({'new_var': 'new_value'}, value_type='str')
        assert 'strRUNTK1' in dispatcher.env
        assert dispatcher.env['strRUNTK1'] == 'new_var=new_value'

    def test_add_val(self, setup):
        dispatcher = setup
        dispatcher.add_val('str', 'new_var', 'new_value')
        assert 'strRUNTK1' in dispatcher.env
        assert dispatcher.env['strRUNTK1'] == 'new_var=new_value'

    def test_create_job(self, setup):
        dispatcher = setup
        dispatcher.create_job()
        print(dispatcher.submit)
        print(dispatcher.sockname)
        print(dispatcher.shellfile)
        print(dispatcher.runfile)
        dispatcher.clean()
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

