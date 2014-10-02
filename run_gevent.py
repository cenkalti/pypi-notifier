#!/usr/bin/env python
from gevent.monkey import patch_all; patch_all()
from gevent.wsgi import WSGIServer
import os
import sys
import pypi_notifier
app = pypi_notifier.create_app(sys.argv[1])
http_server = WSGIServer(('0.0.0.0', int(os.environ.get("PORT", 5000))), app)
http_server.serve_forever()
