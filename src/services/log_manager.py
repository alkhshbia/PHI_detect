import logging
from logging.handlers import RotatingFileHandler
from collections import deque
import os
import threading

class InMemoryLogHandler(logging.Handler):
    """Custom handler that stores logs in memory with thread-safe access."""

    def __init__(self, maxlen=1000):
        super().__init__()
        self.log_buffer = deque(maxlen=maxlen)
        # Use RLock instead of Lock to prevent deadlocks when logging
        # is triggered from within code that already holds the lock
        self._buffer_lock = threading.RLock()

    def emit(self, record):
        """Store log record in memory buffer."""
        try:
            # Use non-blocking acquire to prevent deadlocks with requests library
            if self._buffer_lock.acquire(blocking=False):
                try:
                    log_entry = self.format(record)
                    self.log_buffer.append({
                        'timestamp': record.created,
                        'level': record.levelname,
                        'logger': record.name,
                        'message': log_entry,
                        'raw': record.getMessage()
                    })
                finally:
                    self._buffer_lock.release()
            # If we can't acquire the lock, skip this log entry to avoid deadlock
        except Exception:
            self.handleError(record)

    def get_logs(self, level=None, logger_name=None, limit=None):
        """Retrieve logs with optional filtering."""
        with self._buffer_lock:
            logs = list(self.log_buffer)

        if level:
            logs = [l for l in logs if l['level'] == level]
        if logger_name:
            logs = [l for l in logs if l['logger'] == logger_name]

        if limit:
            logs = logs[-limit:]

        return logs

    def clear_logs(self):
        """Clear all logs from memory."""
        with self._buffer_lock:
            self.log_buffer.clear()

# Global instance
_memory_handler = None

def setup_logging(app):
    """Configure application-wide logging."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # File handler with rotation (10MB max, keep 5 backup files)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)

    # In-memory handler (keep last 1000 log entries)
    global _memory_handler
    _memory_handler = InMemoryLogHandler(maxlen=1000)
    _memory_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    _memory_handler.setFormatter(formatter)

    # Only add handlers to root logger if not already present (avoid duplicates in debug mode)
    root_logger = logging.getLogger()

    # Check if handlers are already attached
    handler_types = [type(h) for h in root_logger.handlers]

    if RotatingFileHandler not in handler_types:
        root_logger.addHandler(file_handler)

    if InMemoryLogHandler not in handler_types:
        root_logger.addHandler(_memory_handler)

    if root_logger.level == logging.NOTSET:
        root_logger.setLevel(logging.INFO)

    return _memory_handler

def get_memory_handler():
    """Get the global in-memory handler instance."""
    return _memory_handler
