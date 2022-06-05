import logging
import logging.config


def generate_logging_config(log_level: str, enable_rich_logs: bool = False) -> dict:
    """Generates logging config.

    Args:
        log_level: Log level
        enable_rich_logs: True to enable "rich" logs (using the rich library). False to
            use the default json logs.

    Returns:
        log config dict.
    """
    log_level = log_level.upper()
    log_handler = "simple"
    if enable_rich_logs:
        log_handler = "rich"

    logger_config = {
        "level": log_level,
        "handlers": [log_handler],
    }

    logging_config = {
        "version": 1,
        "handlers": {
            "simple": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
            "rich": {
                "class": "rich.logging.RichHandler",
                "rich_tracebacks": True,
            },
        },
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s",
            },
        },
        "loggers": {
            "sqlalchemy.engine": logger_config,
            "alembic": logger_config,
        },
        "root": logger_config,
        "disable_existing_loggers": False,
    }

    return logging_config


def init_logging(log_level: str, enable_rich_logs: bool = False):
    """Configures the logger.

    Args:
        log_level: Log level
        enable_rich_logs: True to enable "rich" logs (using the rich library). False to
            use the default json logs.
    """
    logging_config = generate_logging_config(log_level=log_level, enable_rich_logs=enable_rich_logs)
    logging.config.dictConfig(logging_config)
