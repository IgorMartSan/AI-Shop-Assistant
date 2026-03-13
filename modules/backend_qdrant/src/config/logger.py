import os
import logging
import queue
import atexit
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from typing import Any

LOG_QUEUE_SIZE = 10_000
REQUEST_VALIDATION_ERROR_MESSAGE = (
    "Request validation error | method=%s | path=%s | errors=%s"
)

# ✅ guarda referência global para parar no shutdown
_LISTENER: QueueListener | None = None


class ErrorModeFilter(logging.Filter):
    """
    Controls how error messages are displayed.

    Modes:
        - full     → full stacktrace
        - summary  → one-line clean error summary
    """

    def __init__(self, mode: str):
        self.mode = mode.lower()

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno < logging.ERROR:
            return True

        if self.mode == "full":
            return True

        # SUMMARY MODE
        msg = record.getMessage()

        if record.exc_info:
            exc_type = record.exc_info[0].__name__
            record.msg = f"{exc_type}: {msg.splitlines()[-1]}"
            record.args = ()
        else:
            record.msg = msg.splitlines()[-1]
            record.args = ()

        return True


def _stop_listener() -> None:
    global _LISTENER
    try:
        if _LISTENER is not None:
            _LISTENER.stop()
            _LISTENER = None
    except Exception:
        # não deixa shutdown falhar por causa do logger
        pass


def setup_logger(
    container_name: str,
    log_dir: str = "/system_log",
    show_log: bool = True,
    error_mode: str = "full",
) -> None:
    """
    Configure a high-performance, non-blocking logger with optional stacktrace filtering.

    Args:
        container_name (str): Name of the container or service (log file name).
        log_dir (str): Directory where log files will be written.
        show_log (bool): Whether to print logs to stdout.
        error_mode (str): How error messages should be displayed:
            - "full"     → keep full stacktrace
            - "lastline" → keep only the last useful line of the error.

    This logger uses a bounded queue to avoid blocking critical threads.
    """
    global _LISTENER

    os.makedirs(log_dir, exist_ok=True)
    path_log = os.path.join(log_dir, f"{container_name}.log")

    root = logging.getLogger()
    root.handlers.clear()
    root.filters.clear()
    root.setLevel(logging.INFO)

    root.addFilter(ErrorModeFilter(error_mode))

    log_queue = queue.Queue(maxsize=LOG_QUEUE_SIZE)
    root.addHandler(QueueHandler(log_queue))

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(process)d:%(threadName)s | %(name)s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
    )

    handlers = []

    file_handler = RotatingFileHandler(
        path_log, maxBytes=10 * 1024 * 1024, backupCount=1
    )
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    if show_log:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # ✅ se já existe listener (setup_logger chamado de novo), para antes
    if _LISTENER is not None:
        _stop_listener()

    # ✅ cria + guarda referência
    _LISTENER = QueueListener(log_queue, *handlers, respect_handler_level=True)
    _LISTENER.start()

    # ✅ garante stop ao finalizar o Python (evita crash no shutdown)
    atexit.register(_stop_listener)

    logging.info(
        "Logger initialized | name=%s | queue=%s | error_mode=%s",
        container_name,
        LOG_QUEUE_SIZE,
        error_mode,
    )


def log_request_validation_error(
    logger: logging.Logger,
    method: str,
    path: str,
    errors: list[dict[str, Any]],
) -> None:
    logger.exception(
        REQUEST_VALIDATION_ERROR_MESSAGE,
        method,
        path,
        errors,
    )
