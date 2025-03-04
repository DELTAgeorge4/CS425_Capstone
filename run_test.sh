#!/bin/bash
cd ./installation
source venv/bin/activate
cd ..
python3 -m unittest discover -s project_unittesting
