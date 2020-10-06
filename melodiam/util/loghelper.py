from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger

from melodiam import conf


def init_logger() -> Logger:
    logger = getLogger("melodiam")
    if logger.handlers:  # pragma: no cover
        return logger

    handler = StreamHandler()
    fmt = Formatter("%(asctime)s [%(name)s:%(lineno)s] %(levelname)s %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(DEBUG if conf.DEBUG else INFO)
    return logger
