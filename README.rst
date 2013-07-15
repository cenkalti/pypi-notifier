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

Configuration
-------------

Copy ``config.example.py`` as ``config.py`` and fill the values.

Running Web Server
------------------

Web server is run with `gevent <http://www.gevent.org/>`_.
There is a script for running the web server::

    ./run_gevent.py

Flask development server can be run with the following command::

    ./manage.py runserver

Running Jobs
----------------------

This script is run by cron::

    ./run_jobs.sh
