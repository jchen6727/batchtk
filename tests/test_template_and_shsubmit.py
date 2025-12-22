import pytest
import warnings
from batchtk.runtk.submits import Template, SHSubmit

class TestTemplate:
    def test_template_creation(self):
        template = Template("Hello, {name}!", key_args=['name'])
        assert template.template == "Hello, {name}!"
        assert "name" in template.key_args

    def test_template_format(self):
        template = Template("Hello, {name}!")
        formatted = template.format(name="World")
        assert formatted == "Hello, World!"

    def test_template_format_missing_key_warning(self):
        template = Template("Hello, {name}!", key_args=['wrong'])
        with pytest.warns(UserWarning, match="argument 'name' was found in the script"):
            formatted = template.format(wrong_key="World")
        assert formatted == "Hello, {name}!"  # Should return original template with missing key

    def test_template_format_missing_key_warning_fixed(self):
        template = Template("Hello, {name} and {name2}!")
        with pytest.warns(UserWarning, match="argument 'name' was found in the script"):
            formatted = template.format(name2="World")
        assert formatted == "Hello, {name} and World!"

    def test_template_update(self):
        template = Template("Hello, {name}!")
        template.update(name="World")
        assert template.template == "Hello, World!"


class TestSHSubmit:
    def test_shsubmit_creation(self):
        submit = SHSubmit()
        assert submit.command_template.template == "sh {output_dir}/{label}.sh"
        assert "nohup {command}" in submit.script_template.template

    def test_shsubmit_create_job(self):
        submit = SHSubmit()
        submit.create_job(
            project_dir="/tmp",
            output_dir="/tmp/output",
            label="my_job",
            command="echo 'hello'"
        )
        assert submit.command == "sh /tmp/output/my_job.sh"
        assert "cd /tmp" in submit.script
        assert "nohup echo 'hello'" in submit.script
        assert "my_job.sh" in submit.path

    def test_shsubmit_custom_template(self):
        custom_script = "echo {custom_var}"
        submit = SHSubmit(script_template=custom_script, command_template="foo")
        submit.create_job(custom_var="custom_value")
        assert submit.script == "echo custom_value"

    def test_shsubmit_deprecation_warnings(self):
        with pytest.warns(DeprecationWarning, match="submit_template is deprecated"):
            submit = SHSubmit(submit_template="echo 'deprecated'")
        assert submit.command_template.template == "echo 'deprecated'"

        with pytest.warns(DeprecationWarning, match="SUBMIT_TEMPLATE is deprecated"):
            assert SHSubmit.SUBMIT_TEMPLATE is not None

        with pytest.warns(DeprecationWarning, match="SUBMIT_TEMPLATE is deprecated"):
            SHSubmit.SUBMIT_TEMPLATE = "foo"
        assert SHSubmit.COMMAND_TEMPLATE == "foo"
        
        submit = SHSubmit(command_template="bar")
        with pytest.warns(DeprecationWarning, match="'submit_template' attribute is deprecated"):
            submit.submit_template = "bar2"
        assert submit.command_template == "bar2"

        with pytest.warns(DeprecationWarning, match="'submit_template' attribute is deprecated"):
            assert submit.submit_template == "bar2"

        with pytest.warns(DeprecationWarning, match="'submit' attribute is deprecated"):
            submit.submit = "baz"
        assert submit.command == "baz"

        with pytest.warns(DeprecationWarning, match="'submit' attribute is deprecated"):
            assert submit.submit == "baz"
