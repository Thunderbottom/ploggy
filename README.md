# Ploggy

Ploggy is a dead-simple, extensible logging framework for Python. Ploggy handles all the basics of logging, filtering and formatting, and gives you complete control over structuring your own log data.

Ploggy is inspired by [`onelog`](https://github.com/francoispqt/onelog), but intends to not be limited to JSON logging.

## Installation

`ploggy` requires Python 3.7.0+ and can be installed through `pip`:

```
$ python -m pip install --user ploggy
```

Or if you are feeling adventurous:

```
$ python -m pip install git+git://github.com/thunderbottom/ploggy
```

## Usage

### Basic Usage

With ploggy, you are expected to be in-charge of setting up your own logging handler. Although, with that being said, ploggy comes with a demonstrative implementation of a JSON handler which logs the data as, well, _JSON_. This demonstrative implementation strays from the canonical `$timestamp - $LOGLEVEL - $message` convention, partly to showcase what ploggy _can do_, and partly because of personal requirements.

The JSON logging handler outputs the log message to `STDERR`, along with executing custom hook methods and extra parameters. The implementation can be found under [`ploggy.handlers.json`](./ploggy/handlers/json.py), and should be fairly simple to understand. Let's set up an instance of this JSON logging handler. The complete implementation of this example can be found under [`example.py`](./example.py)

First, we create an instance of `JSONHandler`. This inherits the `Handler` base class, and is responsible for formatting the data and the output. There are five log levels available in the base package, in the order of verbosity: `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`. The `JSONHandler` has a default Log Level set to `WARN`, which means that only logs with level `WARN` and above will be handled by this handler. 

```python
handler = JSONHandler()
```

This handler also integrates with the `JSONEntry` class, which contains all the fields for a single line of the log output. With the handler initialized, we now need to set up an instance of the Logger, and register the handler.

The Logger instance requires a scope, which in our case is used to specify an identifier for a part of the application that the logger is running for:

```python
logger = JSONLogger(scope="app_name")
```

One may also specify the log levels that the logger handles. By default, all the log levels are handled:

```python
logger = JSONLogger(levels=[INFO, WARN, ERROR])
```

To register the handler, use the `register()` method. You may attach any number of handlers to a single Logger instance.

```python
handler = JSONHandler()
logger = JSONLogger(scope="app_name")
logger.register(handler)
```

Once the logger is set up and the handler is registered, the application is ready to start logging. To log, specify the log level and the message that needs to be logged:

```python
logger.log(INFO, message="This is an INFO level message.")
# STDERR: {'lvl': 'info', 'line': '/path/to/caller:36', 'msg': 'This is an INFO level message.', 'p': {}, 'sc': 'app_name', 'ts': '2021-02-04 21:26:34.019338'}
```

The output is a JSON containing all the fields defined in the `JSONEntry` class. You can see that the application scope is logged under the `sc` field, and the `p` field is an empty dictionary, since no extra parameters were passed to the logger function. The `ts` field shows the timestamp for the log, which is a `hook` that was registered (along with `line`, and `sc`) in the JSONLogger class. Additional parameters can also be logged, if required:

```python
logger.log(INFO, message="This is an INFO level message.", params={"key": "value"})
# STDERR: {'lvl': 'info', 'line': '/path/to/caller:36', 'msg': 'This is an INFO level message.', 'p': {'key': 'value'}, 'sc': 'app_name', 'ts': '2021-02-04 21:26:34.019338'}
```

As you can see, the `p` field now displays the additional parameters passed to the logger. The same function call can alternatively be written as:

```python
log.info("This is an INFO level message.", params={"key": "value"})
```

This convention can be used for all the log levels that are handled by the `JSONLogger` class.

### Customization

The [`JSON Logger`](./ploggy/handlers/json.py) implementation can be used as an example to set up custom logger implementations. To make things a bit easier, here's another sample implementation with explanation for all the conventions used by this logger:

#### Level

An instance of Level signifies a Log Level, with a string (`name`) mapped to an integer (`val`). This allows us to compare multiple log levels, and decide whether the data needs to be handled and logged by the handler. You may also create your own log level:

```python
# let's create a log level CRITICAL,
# and assign it a value 6, which currently
# is the highest
critical = Level(name="CRITICAL", value=6)
info = Level(name="INFO", value=3)

# comparing these two levels is as easy as:
critical >= info
# OUT: True

# This information is used by the logger to
# check whether the handler is supposed to handle
# the log output for the given log level.
```

#### Entry

Entry contains all the details that are required to create an entry in the Log. You may inherit this class to create your own `Entry`, just like the `JSONEntry` class. Each field signifies a field in the log output:

```python
@dataclass
class JSONEntry(Entry):
    level: Level
    line: str
    message: str
    scope: str
    timestamp: datetime
    params: field(default_factory=dict) = None
```

#### Hooks

Hooks are methods that execute whenever `log()` is called. Hooks need to be defined as a dictionary, with string keys and functions as values. These hooks then need to be added to the `Logger` class. The output of these hook executions are passed to the `Entry` class as kwargs, and can be then utilized in the `Handler`. For example:

```python
logger.hooks = {
    # An instance of the logger is passed to each
    # hook function, which can be used to further
    # manipulate data in the function
    "timestamp": (lambda l: str(datetime.now()))
}

# OUT: {"timestamp": "2021-02-04 21:26:34.019338"}
```

#### Handler

Handler is the base class for formatting and outputting the log `Entry`. A `Handler` requires a list of Log Levels that it will handle, and a `pipe`, which specifies the log output. By default, the base Handler implementation uses `STDERR` for outputting logs. The [`JSONHandler`](./ploggy/handlers/json.py#L60) implementation can be used as an example to set up a custom log Handler.

#### Logger

Logger is the base class for the Logging interface. Logger requires `Handlers` to be registered, and a list of log levels that the logging interface will handle. Any number of Handlers and Log Levels can be registered to an instance of `Logger`. Optionally, `Hooks` can be attached to a logger, which will execute on every `log()` call. The [`JSONLogger`](./ploggy/handlers/json.py#L40) implementation can be used an example to set up a custom Logger.

#### Example Implementation

Let's set up a logger that logs incoming requests:

```python
@dataclass
class RequestEntry(Entry):

    level: Level
    message: str
    timestamp: datetime
    params: field(default_factory=dict) = None


class RequestLogger(Logger):

    Entry: Type[Entry] = RequestEntry

    def __init__(self, scope: str) -> None:
        super().__init__()
        self.hooks = {
            "timestamp": (lambda l: datetime.now()),
        }


@dataclass
class RequestHandler(Handler):

    level: Level = WARN
    pipe: IO = stderr

    def format(self, entry: RequestEntry) -> Dict[str, Any]:
        params = {}
        pstr = ""
        if entry.params is not None:
            pstr = ",".join([f"{key}={val}" for key, val in entry.params.items()])

        return f"{entry.timestamp} - lvl={entry.level}, message={entry.message}, params=\{{pstr}\}"
```

To log data, set up the logger in your application:

```python
handler = RequestHandler(level=INFO)
# Or to set up a file ouput, pass a file buffer to as `pipe`:
# file = open("/some/path/to/log", "w")
# handler = RequestHandler(level=INFO, pipe=file)
logger = RequestLogger()
logger.register(handler)

logger.error(
    "An error occurred while handling request",
    params={
        "method": "GET",
        "endpoint": "/endpoint",
        "error_type": "general",
    }
)

# STDERR: 2021-02-04 21:26:34.019338 - lvl=ERROR, message=An error has occurred while handling request,
# params={method=GET,endpoint=/endpoint,error_type=general}
```

## Contributions

Pull Requests for features, bug fixes are welcome. Feel free to open an issue for bugs and discussions on the logger functionality.

## License

```
MIT License

Copyright (c) 2021 Chinmay Pai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
