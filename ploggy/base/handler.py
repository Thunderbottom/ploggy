from typing import IO
from dataclasses import dataclass
from sys import stderr

from .entry import Entry
from .levels import Level, INFO


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
        print(self.format(entry), file=self.pipe, flush=True)

    def format(self, entry: Entry) -> str:
        return entry.message
