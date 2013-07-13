from gevent.monkey import patch_all; patch_all()
from gevent.wsgi import WSGIServer
from pypi_notifier import create_app
app = create_app('ProductionConfig')
http_server = WSGIServer(('0.0.0.0', 5001), app)
http_server.serve_forever()
