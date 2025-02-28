# Developed by Nicholas Katsaros
#!/bin/bash

# Variables
SERVICE_NAME="packet_capture"
SCRIPT_PATH="~/CS425_Capstone/nicks-testing/capture_starter.py"
WORKING_DIR="~/CS425_Capstone/nicks-testing/"
PYTHON_EXEC="/usr/bin/python3"
LOG_FILE="/var/log/${SERVICE_NAME}.log"

# Ensure the log file exists
sudo touch "$LOG_FILE"
sudo chmod 644 "$LOG_FILE"

# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Python Service for $SCRIPT_PATH
After=network.target

[Service]
Type=simple
ExecStart=$PYTHON_EXEC $SCRIPT_PATH
WorkingDirectory=$WORKING_DIR
Restart=always
User=$USER
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Service $SERVICE_NAME created and started."
echo "Logs can be found at $LOG_FILE"
