#!/bin/bash -e
#
# This script is intended to run from cron.

LOCKFILE="/srv/http/pypi-notifier/run_jobs.lock"

# Directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd ${DIR}

source /home/cenk/.virtualenvs/pypi-notifier/bin/activate
export PYPI_NOTIFIER_CONFIG=ProductionConfig

(
    flock -x -w 10 200           # Wait for lock for 10 seconds

    ./manage.py update_repos     # Fetches requirements from GitHub
    ./manage.py update_packages  # Checks latest versions from PyPI
    ./manage.py send_emails      # Notifies users about updates

) 200>$LOCKFILE
