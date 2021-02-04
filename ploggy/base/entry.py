from dataclasses import dataclass
from typing import Any

from .levels import Level


@dataclass
class Entry:
    """
    Base class for generating a Log Entry. Requires a Log Level
    and the message to be logged. This class is not intended to be
    called on its own, and should rather be used from within the Logger
    class.

    Example:
        >>> INFO = Level(name="INFO", val=1)
        >>> entry = Entry(level=INFO, message="This is an info level entry.")
        >>> entry
        Entry(level=Level(name="INFO", val=1), message="This is an info level entry.")
    """

    level: Level
    message: Any
