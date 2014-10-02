PyPI Notifier
=============

http://www.pypi-notifier.org

Watches your ``requirements.txt`` files and notifies you via email when
a project is updated.

Requirements
------------

Python 2.7 is required to run PyPI Notifier. Install the project dependencies
with::

    pip install -r requirements.txt

Running
-------

Web server is run with `gevent <http://www.gevent.org/>`_.
There is a script for running the web server::

    ./run_gevent.py development

Flask development server can be run with the following command::

    ./manage.py runserver

This task is run by scheduler hourly to send emails::

    ./manage.py --config development hourly
