#!/usr/bin/env bash
set -e

# go to your app dir
cd /opt/total_virus

# install any missing deps
./install_dependencies.sh

# activate the venv
source ./venv/bin/activate

# hand off to Python
exec python3 -m main