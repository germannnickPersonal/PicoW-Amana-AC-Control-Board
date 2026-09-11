import sys
import io

from logger import Logger

class ErrorLogger(Logger):
    def __init__(self):
        super().__init__(
            max_entries=50,
            filename = "ErrorLog.txt",
            separator = "\n___ERROR___\n"
            )

    def log(self, source, error):
        message = ""

        if isinstance(error, Exception):
            buffer = io.StringIO()
            sys.print_exception(error, buffer)
            message = "{}: {}\n".format(
                  source,
                  buffer.getvalue()
                  )
        else:
            message = "{}: {}\n".format(
                source, error)

        super().log(message)

logger = ErrorLogger()