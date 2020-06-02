import os
import logging

level = os.getenv('PYPI_NOTIFIER_LOGGING_LEVEL')
if level:
    logging.basicConfig(level=getattr(logging, level.upper()))
