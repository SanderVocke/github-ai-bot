import logging

def stream_and_level_for_all_loggers(level=logging.DEBUG):
    for name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(logging.StreamHandler())