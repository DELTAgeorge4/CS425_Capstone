import os
import sys

def create_service(interface):
    SERVICE_NAME = "nss_sniffer_" + interface  # format for service names
    SERVICE_FILE = f"/etc/systemd/system/{SERVICE_NAME}.service"
    SCRIPT_RELATIVE_PATH = "capture_starter.py"
    USER = "root"

    # Resolve absolute path
    SCRIPT_ABS_PATH = os.path.abspath(SCRIPT_RELATIVE_PATH)
    WORKING_DIR = os.path.dirname(SCRIPT_ABS_PATH)

    SERVICE_CONTENT = f"""[Unit]
Description=NSS Packet Sniffer
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/CS425_Capstone/nicks-testing/capture_starter.py eth0
WorkingDirectory=/home/CS425_Capstone/nicks-testing
Restart=always
User=root
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
"""

    try:
        # Write the systemd service file
        with open("temp_service.service", "w") as f:
            f.write(SERVICE_CONTENT)

        # Move it to /etc/systemd/system (requires sudo)
        os.system(f"sudo mv temp_service.service {SERVICE_FILE}")
        os.system(f"sudo chmod 644 {SERVICE_FILE}")
        os.system(f"sudo chown root:root {SERVICE_FILE}")

        # Reload systemd, enable, and start the service
        os.system("sudo systemctl daemon-reload")
        os.system(f"sudo systemctl enable {SERVICE_NAME}")
        os.system(f"sudo systemctl start {SERVICE_NAME}")

        print(f"Service '{SERVICE_NAME}' created and started successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments provided.")
        exit(1)
    if len(sys.argv) > 2:
        print("Too many arguments provided")
        exit(1)
    create_service(sys.argv[1])
