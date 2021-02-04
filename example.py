import time
from random import randint
from ploggy.handlers.json import JSONHandler, JSONLogger

handler = JSONHandler()

logger = JSONLogger(scope="test app")
logger.handlers.append(handler)


def log_test():
    while True:
        logger.error(
            "this is a generic error",
            params={
                "error_type": "general",
                "random_number": randint(10, 100),
            },
        )
        logger.warn(
            "this is a warning, be warned",
            params={
                "error_type": "db",
                "random_db_number": randint(1, 10),
            },
        )
        # The following call  won't be logged as the
        # registered handler's default log level is
        # WARN, which is above INFO in terms of verbosity.
        logger.info("this is an info, dont be warned.")
        time.sleep(5)


if __name__ == "__main__":
    log_test()
