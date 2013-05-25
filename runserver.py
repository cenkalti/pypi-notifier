#!/usr/bin/env python
from deli import create_app, db
from deli.config import DevelopmentConfig

app = create_app(DevelopmentConfig)
with app.app_context():
    db.create_all()

app.run(host='0.0.0.0', port=5000, debug=True)
