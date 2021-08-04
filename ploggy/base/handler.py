import os
import sys
import io
import traceback

from typing import IO
from dataclasses import dataclass
from sys import stderr

from .entry import Entry
from .levels import Level, INFO


def fake_function():
    pass


_srcfile = os.path.normcase(fake_function.__code__.co_filename)


# Ref: https://github.com/python/cpython/blob/main/Lib/logging/__init__.py#L162
if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
else: #pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back


def find_caller(stack_info=False, stacklevel=1):
    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.

    ref: https://github.com/python/cpython/blob/main/Lib/logging/__init__.py#L1553
    """
    f = currentframe()
    if f is not None:
        f = f.f_back
    orig_f = f
    while f and stacklevel > 1:
        f = f.f_back
        stacklevel -= 1
    if not f:
        f = orig_f
    rv = "(unknown file)", 0, "(unknown function)", None
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename == _srcfile:
            f = f.f_back
            continue
        sinfo = None
        if stack_info:
            sio = io.StringIO()
            sio.write('Stack (most recent call last):\n')
            traceback.print_stack(f, file=sio)
            sinfo = sio.getvalue()
            if sinfo[-1] == '\n':
                sinfo = sinfo[:-1]
            sio.close()
        rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
        break
    return rv

@dataclass
class Handler:
    """
    A class for handling message logging. Requires a default
    Log Level to be set and an IO pipe to publish the output
    defaults to `sys.stderr`.
    """

    level: Level = INFO
    pipe: IO = stderr

    def log(self, entry: Entry) -> None:
        try:
            fn, lno, func, _ = find_caller()
        except ValueError:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"

        line_ctx = f"{fn}:{lno}:{func}"

        print(self.format(line_ctx, entry), file=self.pipe, flush=True)

    def format(self, line_ctx: str, entry: Entry) -> str:
        return entry.message
