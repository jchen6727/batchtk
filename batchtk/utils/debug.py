from logging import Logger, StreamHandler, FileHandler, Formatter
from datetime import datetime
from typing import Optional
from sys import stdout
from batchtk.utils import _get_obj_args
import _io

class PrintUtil(Logger):
    def __init__(
            self,
            name: Optional[str] = 'batchtk',
            file_out: Optional[str] = None,
            file_level: Optional[int] = 10, # DEBUG will be printed to filename
            console_level: Optional[int] = 30, # WARNING will be printed to console
            console_out: Optional[_io.TextIOWrapper] = stdout,
            format_str: Optional[str] = '%(message)s',
            ):
        super().__init__(name)
        self.instance_kwargs = _get_obj_args(**locals())
        handler = StreamHandler(console_out)
        handler.setLevel(console_level)
        handler.setFormatter(Formatter(format_str))
        self.addHandler(handler)
        if file_out == None:
            file_out = "{}_{}".format(name, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        handler = FileHandler(file_out)
        handler.setLevel(file_level)
        handler.setFormatter(Formatter(format_str))

    def debug(self, *args, **kwargs):
        """Logs a debug message."""
        self.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        """Logs an info message."""
        self.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """Logs a warning message."""
        self.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """Logs an error message."""
        self.error(*args, **kwargs)
