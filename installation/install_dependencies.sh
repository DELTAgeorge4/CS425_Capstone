#!/bin/bash
echo "Installing dependencies..."
python3 -m venv venv  # Create a virtual environment
source venv/bin/activate  # Activate the virtual environment
pip install psycopg2-binary fastapi uvicorn
pip install -r requirements.txt  # Install dependencies
echo "Dependencies installed successfully."
