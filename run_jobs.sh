#!/bin/bash -e

# Directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd ${DIR}

./manage.py update_repos     # Fetches requirements from GitHub
./manage.py update_packages  # Checks latest versions from PyPI
./manage.py send_emails      # Notifies users about updates
