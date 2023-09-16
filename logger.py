from logging import getLogger, Formatter, StreamHandler

# Subs for logging.LEVEL values
LOG_LEVELS = { 
  'debug': 10,
  'info': 20,
  'warning': 30,
  'error': 40,
  'critical': 50
}

def configure_logger(module, level):
  ## Logging Configuration
  # Main
  level = LOG_LEVELS[level]
  logger = getLogger(module)
  logger.setLevel(level)
  formatter = Formatter("%(asctime)s-%(levelname)s: %(message)s", "%H:%M:%S")
  sh = StreamHandler()
  sh.setFormatter(formatter)
  logger.addHandler(sh)
  return logger