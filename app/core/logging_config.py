import logging
import sys

from app.core.config import settings


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "%(message)s"
)


def configure_logging() -> None:
    log_level = settings.LOG_LEVEL.upper()
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout)
    ]

    if settings.LOG_FILE:
        try:
            handlers.append(
                logging.FileHandler(
                    settings.LOG_FILE,
                    encoding="utf-8",
                )
            )
        except OSError:
            pass

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=handlers,
        force=True,
    )

    logging.getLogger("uvicorn.access").setLevel(
        logging.WARNING
    )
