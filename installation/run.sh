#!/bin/bash

./install_dependencies.sh
echo "running chmod"
chmod +x ../backend/restartSuricata.sh
source ./venv/bin/activate  # Ensure the correct path to 'venv/bin/activate'
cd ../backend
pwd
fastapi dev --port 8000
