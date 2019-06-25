import logging, os
logger = logging.getLogger()
logger.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'ERROR').upper()))
