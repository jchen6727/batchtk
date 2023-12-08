import pytest
from pubtk.runtk.dispatchers import Dispatcher

class TestDispatcher:
    @pytest.fixture
    def setup(self):
        dispatcher = Dispatcher(env={'test': 'value'}, grepstr='RUN', gid='123')
        return dispatcher

    def test_init(self, setup):
        dispatcher = setup
        assert dispatcher.env == {'test': 'value'}
        assert dispatcher.grepstr == 'RUN'
        assert dispatcher.gid == '123'

    def test_add_dict(self, setup):
        dispatcher = setup
        dispatcher.add_dict({'new_var': 'new_value'}, value_type='str')
        assert 'strRUN1' in dispatcher.env
        assert dispatcher.env['strRUN1'] == 'new_var=new_value'

    def test_add_val(self, setup):
        dispatcher = setup
        dispatcher.add_val('str', 'new_var', 'new_value')
        assert 'strRUN1' in dispatcher.env
        assert dispatcher.env['strRUN1'] == 'new_var=new_value'

    # Add more tests for other methods...