from logging import Logger, StreamHandler, Formatter
from sys import stdout
import _io

class PrintUtil(Logger):
    def __init__(
            self,
            name: str = 'batchtk',
            file_out: str = '',
            file_level: int = 10, # DEBUG will be printed to filename
            console_level: int = 30, # WARNING will be printed to console
            console_out: _io.TextIOWrapper = stdout,
            format_str: str = '%(message)s',
            ):
        super().__init__(name)
        self.args = file_level
        self.console_level = console_level
        self.file = file_out
        self.io = console_out
        self.format_str = format_str
        handler = StreamHandler()


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