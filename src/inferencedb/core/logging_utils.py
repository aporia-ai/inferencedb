import logging
import logging.config


def generate_logging_config(log_level: str) -> dict:
    """Generates logging config.

    Args:
        log_level: Log level

    Returns:
        log config dict.
    """
    log_level = log_level.upper()
    log_handler = "simple"

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


def init_logging(log_level: str):
    """Configures the logger.

    Args:
        log_level: Log level
    """
    logging_config = generate_logging_config(log_level=log_level)
    logging.config.dictConfig(logging_config)
