PyPI Notifier
=============

http://www.pypi-notifier.org

Watches your ``requirements.txt`` files and notifies you via email when
a requirement is updated.

.. image:: https://travis-ci.org/cenkalti/pypi-notifier.svg?branch=master
    :target: https://travis-ci.org/cenkalti/pypi-notifier

Requirements
------------

Python 3 is required to run PyPI Notifier. Install the project's dependencies
with::

    pip install -r requirements.txt

Running
-------

First, add your Github client credentials into development config in `config.py`.

Then, set your config env var in your shell::

    export PYPI_NOTIFIER_CONFIG=development

Create necessary tables for the application::

    flask init-db

Web server is run with `gevent <http://www.gevent.org/>`_.
There is a script for running the web server::

    ./run_gevent.py

Flask development server can be run with the following command::

    flask run

An hourly task is run by a scheduler to send emails::

    flask hourly
