import sys

class Logger:
    def __init__(self):
        self._handlers = {}

    def add(self, sink, level="INFO", format="{time} {message}", **kwargs):
        """Add a handler to the logger."""
        handler_id = len(self._handlers)
        self._handlers[handler_id] = sink
        return handler_id

    def info(self, message, *args, **kwargs):
        """Log a message with 'INFO' level."""
        self._log("INFO", message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Log a message with 'ERROR' level."""
        self._log("ERROR", message, *args, **kwargs)

    def _log(self, level, message, *args, **kwargs):
        print(f"[{level}] {message}")

logger = Logger()
