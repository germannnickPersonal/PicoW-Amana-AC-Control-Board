import sys
import time

MAX_ERRORS = 50
LOG_FILE = "error_log.txt"
SEPARATOR = "\n---ERROR---\n"

class ErrorLogger:
    def __init__(self, filename=LOG_FILE, max_errors=MAX_ERRORS):
        self.filename = filename
        self.max_errors = max_errors

    def log(self, source, error):
        try:
            # Read existing log entries
            try:
                with open(self.filename, "r") as file:
                    contents = file.read()
            except OSError:
                contents = ""

            # Split the file into errors
            if contents:
                entries = contents.split(SEPARATOR)
            else:
                entries = []

            if len(entries) >= self.max_errors:
                entries = entries[-(self.max_errors -1):]

            with open(self.filename, "w") as file:
                for entry in entries:
                    if entry.strip():
                        file.write(entry)
                        file.write(SEPARATOR)
                uptime = time.ticks_ms() // 1000
                if isinstance(error, Exception):
                    file.write(
                        "[{}sec] {}:\n".format(uptime, source)
                    )
                    sys.print_exception(error, file)
                else:
                    file.write(
                        "[{} sec] {}: {}\n".format(
                            uptime, source, error
                        )
                    )

        except Exception:
            # Don't crash it on error logging
            pass

    def read(self):
        try:
            with open(self.filename, "r") as file:
                return file.read()
        except OSError:
            return ""


logger = ErrorLogger()