from __future__ import annotations
from functools import lru_cache, partial
from typing import Any, Callable, Dict, List, Type

from .levels import Level, DefaultLevels
from .handler import Handler
from .entry import Entry


class Logger:
    """
    Base class for the Logging interface. Requires handlers
    to be attached, and a list of Log levels that this interface
    will handle. Any number of Handlers and Log Levels can be attached
    to a Logger instance.

    Example:
        >>> handler = Handler()  # can be a custom handler
        >>> logger = Logger()
        >>> logger.append(handler)
        >>> logger.log(INFO, "This is an info level entry.")
        This is an info level entry.

    If the handler does not handle a particular log level, it will be skipped.

    Example:
        Considering log level of WARN > INFO
        >>> handler = Handler(level=WARN)
        >>> logger.register(handler)
        >>> logger.log(INFO, "This is an info level entry.")
        # No output will be generated, since the handler only handles
        # log levels of WARN and above.

    The log function can also be called with a log level attribute:

    Example:
        >>> logger.error("This is an error message.")

    The logger can also execute hooks on each function call. The output
    of these hooks are passed to the handler as kwargs.

    These can then be handled by custom implementations of Entry and Handler.

    Example:
        NOTE: The `run_hooks()` function call passes self as a parameter
              to the hook, so anything passed to the logger function can be
              used within the hook function.

        In the example, lambda will have an input param `t`
        >>> logger.hooks = {
            "timestamp": (lambda t: datetime.now())
        }
        >>> logger.info("Let's log with a timestamp.")
        2021-02-04 19:22:42.409301 - Let's log with a timestamp.
    """

    handlers: List[Handler] = []
    # default to all logging levels
    levels: List[Level] = DefaultLevels

    hooks: Dict[str, Callable[[], Any]] = None
    Entry: Type[Entry] = Entry
    exit_on: Level = None

    def _run_hooks(self) -> Dict[str, Any]:
        """
        Executes all hooks attached to the logger instance, and returns a
        dictionary with the hook key and the output value of the executed
        function. This dictionary is then passed to the handler as kwargs.

        Each hook call is passed an instance of `self`, so that the logging
        input can be utilized by the hook functions.

        Example Hooks Structure:

            {
                "timestamp": (lambda t: str(datetime.now())),
                "key": function_call,
            }

        This will result in:

            {
                "timestamp": "2021-02-04 19:22:42.409301",
                "key": "function_output"
            }
        """
        if self.hooks is not None:
            return dict(
                zip(
                    self.hooks.keys(), map(lambda hook: hook(self), self.hooks.values())
                )
            )
        return {}

    def exit_handler(self) -> None:
        """
        Handles exit on error. Requires `exit_on` to be set to a
        valid Log Level
        """
        pass

    def log(self, level: Level, message: Any, **kwargs) -> None:
        """
        Calls `log()` and sends the message on each Handler
        that qualifies for the specified log level.
        """
        entry = self.Entry(level=level, message=message, **self._run_hooks(), **kwargs)
        for handler in self.handlers:
            if entry.level >= handler.level:
                handler.log(entry)

        # call exit_handler if exit_on level is defined and
        # the current log level matches the exit_on log level
        if self.exit_on is not None and self.exit_on == level:
            self.exit_handler()

    def register(self, handler: Handler) -> None:
        """
        Registers the Handler with the logger.
        """
        if handler not in self.handlers:
            self.handlers.append(handler)

    # functools.lru_cache ensures that the output is cached.
    # Caching reduces execution time for repeated calls to the function.
    # The default maxsize of 128 should be sane and safe to use.
    @property
    @lru_cache
    def _levels(self) -> Dict[str, Level]:
        """
        Map log levels in lowercase to their levels. Used for `__getattr__()`
        """
        return {level.name.casefold(): level for level in self.levels}

    @lru_cache
    def __getattr__(self, name: str) -> Any:
        """
        Check whether the level attribute exists in the logger, and call
        log() for that particular level.

        logger.info("message") => logger.log(INFO, "message")
        """
        try:
            return partial(self.log, self._levels[name])
        except KeyError:
            raise AttributeError(
                f"'{self._class__.__name__}' object has no attribute '{name}'"
            )
