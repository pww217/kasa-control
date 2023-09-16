import logging

LOG_LEVELS = { 
  'debug': logging.DEBUG,
  'info': logging.INFO,
  'warning': logging.WARNING,
  'error': logging.ERROR,
  'critical': logging.CRITICAL
}

def configure_logger(module, level):
  ## Logging Configuration
  # Main
  level = LOG_LEVELS[level]
  logger = logging.getLogger(module)
  logger.setLevel(level)
  formatter = logging.Formatter("%(asctime)s-%(levelname)s: %(message)s", "%H:%M:%S")
  sh = logging.StreamHandler()
  sh.setFormatter(formatter)
  logger.addHandler(sh)
  return logger