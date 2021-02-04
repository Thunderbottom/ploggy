from dataclasses import dataclass, field
from datetime import datetime
from inspect import stack
from sys import stderr
from typing import Any, Dict, IO, Type

from ..base.handler import Handler
from ..base.levels import Level, WARN
from ..base.logger import Logger
from ..base.entry import Entry


@dataclass
class JSONEntry(Entry):
    """
    JSONEntry inherits the Entry base class to implement a
    custom logging handler, containing details that include
    the caller details, app scope, timestamp, and additional
    parameters passed to the logger.

    Attributes:
        level:     The log level for this Entry.
        line:      `stack()` containing the current caller details.
        message:   The message to log through the logger.
        scope:     The application scope for which the message is being
                   logged.
        timestamp: The log timestamp.
        params:    Additional parameters passed to the logging handler.

    """

    level: Level
    line: str
    message: str
    scope: str
    timestamp: datetime
    params: field(default_factory=dict) = None


class JSONLogger(Logger):
    """
    JSONLogger inherits the Logger base class. This class adds custom
    hooks to the logging output.
    """

    Entry: Type[Entry] = JSONEntry
    scope: str = "general"

    def __init__(self, scope: str) -> None:
        super().__init__()
        self.scope = scope
        self.hooks = {
            "timestamp": (lambda l: datetime.now()),
            "line": (lambda l: stack()),
            "scope": (lambda l: self.scope),
        }


@dataclass
class JSONHandler(Handler):
    """
    JSONHandler inherits the Handler base class, and uses JSONEntry to
    output the log data as a JSON. The default log level is set to WARN,
    and the logs are written to `sys.stderr()`.

    Example:
        >>> handler = JSONHandler()
        >>> logger = JSONLogger(scope="app")
        >>> logger.handlers.append(handler)
        >>> logger.warn("This is a warning, be warned", params={"warn": True})
        {
            "lvl": "warn",
            "line": "/path/to/file.py:10",
            "msg": "This is a warning, be warned",
            "p": {
                "warn": "True",
            },
            "sc": "app",
            "ts": "2021-02-04 19:22:42.409301",
        }
    """

    level: Level = WARN
    pipe: IO = stderr

    def format(self, entry: JSONEntry) -> Dict[str, Any]:
        # caller holds the stack entry for the calling
        # function. We skip the first 5 frames cause they
        # consist of calls internal to the logging library.
        caller = entry.line[5]
        params = {}
        if entry.params is not None:
            params = {str(key): str(val) for key, val in entry.params.items()}

        return {
            "lvl": entry.level.name.casefold(),
            "line": f"{caller.filename}:{caller.lineno}",
            "msg": entry.message,
            "p": params,
            "sc": entry.scope,
            "ts": str(entry.timestamp),
        }
