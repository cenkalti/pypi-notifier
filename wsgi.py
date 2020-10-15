import os
from pypi_notifier.app import create_app
app = create_app(os.environ['PYPI_NOTIFIER_CONFIG'])
