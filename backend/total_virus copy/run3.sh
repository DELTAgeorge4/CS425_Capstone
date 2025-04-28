#!/bin/bash

python3 -m venv venv  # Create a virtual environment
source venv/bin/activate  # Activate the virtual environment
./install_dependencies.sh
# echo "running chmod"
# chmod +x ../backend/restartSuricata.sh
# source ./venv/bin/activate  # Ensure the correct path to 'venv/bin/activate'
echo "current directory"
pwd
python3 -m main
#uvicorn /home/CS425_Capstone/backend/client_api/main:app --host 0.0.0.0 --port 8001