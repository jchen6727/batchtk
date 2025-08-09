from logging import Logger, StreamHandler, FileHandler, Formatter
from datetime import datetime
from typing import Optional
from sys import stdout
from batchtk.utils import _get_obj_args
import _io
#Custom ScriptLogger
class ScriptLogger(Logger):
    def __init__(
            self,
            name: Optional[str] = 'batchtk',
            file_out: Optional[str|list] = None, # Anything evaluating to false -> no file output, True -> defauult
            file_level: Optional[int|list] = 10, # DEBUG will be printed to filename
            console_level: Optional[int] = 30, # WARNING will be printed to console
            console_out: Optional[_io.TextIOWrapper] = stdout,
            format_str: Optional[str] = '%(message)s',
            **kwargs,
            ):
        super().__init__(name, **kwargs)
        self.instance_kwargs = _get_obj_args(**locals())
        handler = StreamHandler(console_out)
        handler.setLevel(console_level)
        handler.setFormatter(Formatter(format_str))
        super().addHandler(handler)
        if not file_out:
            return
        if file_out is True:
            file_out = "{}_{}".format(name, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        handler = FileHandler(file_out)
        handler.setLevel(file_level)
        handler.setFormatter(Formatter(format_str))
        super().addHandler(handler)

    def debug(self, *args, **kwargs):
        """
        Logs a debug message:
        msg: str - the log message, any object that can be converted to a string
        exc_info: bool - if True, the traceback of the current exception will be added to the log message, defaults to False
        stack_info: bool - if True, the stack trace of the current stack frame will be added to the log message, defaults to False
        extra: dict - any additional information to be added to the log message, defaults to None
        stacklevel: int - the stack level of the log message, defaults to 1, i.e. the log message is created at the call site of this function
        """
        super().debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        """
        Logs an info message:
        msg: str - the log message, any object that can be converted to a string
        exc_info: bool - if True, the traceback of the current exception will be added to the log message, defaults to False
        stack_info: bool - if True, the stack trace of the current stack frame will be added to the log message, defaults to False
        extra: dict - any additional information to be added to the log message, defaults to None
        stacklevel: int - the stack level of the log message, defaults to 1, i.e. the log message is created at the call site of this function
        """
        super().info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """
        Logs a warning message:
        msg: str - the log message, any object that can be converted to a string
        exc_info: bool - if True, the traceback of the current exception will be added to the log message, defaults to False
        stack_info: bool - if True, the stack trace of the current stack frame will be added to the log message, defaults to False
        extra: dict - any additional information to be added to the log message, defaults to None
        stacklevel: int - the stack level of the log message, defaults to 1, i.e. the log message is created at the call site of this function
        """
        super().warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """
        Logs an error message:
        msg: str - the log message, any object that can be converted to a string
        exc_info: bool - if True, the traceback of the current exception will be added to the log message, defaults to False
        stack_info: bool - if True, the stack trace of the current stack frame will be added to the log message, defaults to False
        extra: dict - any additional information to be added to the log message, defaults to None
        stacklevel: int - the stack level of the log message, defaults to 1, i.e. the log message is created at the call site of this function
        """
        super().error(*args, **kwargs)
