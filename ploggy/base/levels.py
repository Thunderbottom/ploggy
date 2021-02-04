from __future__ import annotations
from typing import List
from dataclasses import dataclass


@dataclass
class Level:
    """
    A class describing Log levels, with each log level
    mapped to an integer value.

    Usage:
        >>> levels = Level.init(["DEBUG", "INFO"])
        >>> levels
        [Level(name='DEBUG', val=0), Level(name='INFO', val=1)]
    """

    name: str
    val: int

    # dunder functions for Level comparison
    # Required by logging Handlers to log only above
    # a certain logging level, which is defined in the Handler.
    #
    # Example:
    #    >>> warn = Level(name="WARN", val=2)
    #    >>> info = Level(name="INFO", val=1)
    #    >>> info > warn
    #    false
    #
    # In such cases, if the Handler is defined with a log level
    # `WARN`, then the log data with log level `INFO` will not be
    # logged by the handler.
    def __ge__(self, lvl: Level) -> bool:
        return self.val >= lvl.val

    def __gt__(self, lvl: Level) -> bool:
        return self.val > lvl.val

    def __le__(self, lvl: Level) -> bool:
        return self.val <= lvl.val

    def __lt__(self, lvl: Level) -> bool:
        return self.val < lvl.val

    @classmethod
    def init(cls, levels: List[str]) -> List[Level]:
        """
        Initializes a list of Log Levels
        """
        return [cls(lvl, val) for val, lvl in enumerate(levels)]


# Initialize a set of default levels, ready to be imported and used.
DefaultLevels = Level.init(["DEBUG", "INFO", "WARN", "ERROR", "FATAL"])
DEBUG = DefaultLevels[0]
INFO = DefaultLevels[1]
WARN = DefaultLevels[2]
ERROR = DefaultLevels[3]
FATAL = DefaultLevels[4]
