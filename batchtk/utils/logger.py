from logging import Logger, StreamHandler, FileHandler, Formatter, getLogger
from datetime import datetime
from typing import Optional
from sys import stdout
import _io


def create_logger(
        name: Optional[str] = 'batchtk',
        file_out: Optional[str|list] = None, # Anything evaluating to false -> no file output, True -> defauult
        file_level: Optional[int|list] = 10, # DEBUG will be printed to filename
        console_level: Optional[int] = 30, # WARNING will be printed to console
        console_out: Optional[_io.TextIOWrapper] = stdout,
        format_str: Optional[str] = '%(message)s',
        **kwargs,
        ) -> Logger:
    """
    Factory function to create a logger instance.
    """
    logger = getLogger(name)
    logger.setLevel(min(file_level if file_out else console_level, console_level))

    # Avoid adding handlers if they already exist
    if logger.hasHandlers():
        return logger

    handler = StreamHandler(console_out)
    handler.setLevel(console_level)
    handler.setFormatter(Formatter(format_str))
    logger.addHandler(handler)
    if not file_out:
        return logger
    if file_out is True:
        file_out = "{}_{}".format(name, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    handler = FileHandler(file_out)
    handler.setLevel(file_level)
    handler.setFormatter(Formatter(format_str))
    logger.addHandler(handler)
    return logger
