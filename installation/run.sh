#!/bin/bash

./install_dependencies.sh
chmod +x ../backend/restartSuricata.sh
source ./venv/bin/activate  # Ensure the correct path to 'venv/bin/activate'
cd ..
pwd
fastapi dev
