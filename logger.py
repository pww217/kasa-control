from logging import getLogger, Formatter, StreamHandler


def configure_logger(module, level):
    ## Logging Configuration
    # Main
    logger = getLogger(module)
    logger.setLevel(level)
    formatter = Formatter("%(levelname)s:     %(message)s")
    sh = StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger
