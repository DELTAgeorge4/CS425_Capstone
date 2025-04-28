# config.py

# Change to path where .json logs get placed from suricata, typically /ver/logs/suricata/eve.json
SURICATA_LOG_FILE = "/home/CS425_Capstone/Georges_Scripts/Suricata/Suricata_Logs/eve.json"

# Topology config
# Network topology discovery settings
TOPOLOGY_HOSTS = ['192.168.14.1']  # Add your router/switch IP here
TOPOLOGY_COMMUNITY = 'public'
TOPOLOGY_SNMP_VERSION = 1  # 0 for v1, 1 for v2c


# Honeypot config
HONEYPOT_TARGET_IPS = "192.168.14.14"
HONEYPOT_TARGET_PORTS = [444]

# SNMP Clients formatable via 192.168.1.1 or 192.168.1.1/24
SNMP_HOSTS = ["192.168.14.14", "192.168.14.11"]

# Secify the amount of threads you want snmp to use.
SNMP_WORKERS = 4

# Define tables you want to incude in INTERACT_W_TABLES.PY script
TESTING_TABLES = ["snmp_metrics", "suricata", "honeypot"]

# Preconfigured Database Info, SHOULD NOT TOUCH UNLESS MANUALLY CHANGED
DB_HOST = "192.168.14.14"
DB_NAME = "nss"
DB_USER = "postgres"
DB_PASSWORD = "password123" # Update with password set up by Make_Tables.py

# SNMP Settings for email alerts
SMTP_SERVER = "smtp.gmail.com"  # Use email SMTP server
SMTP_PORT = 587
EMAIL_USER = "email123@email.com"  # Your email address
EMAIL_PASSWORD = "password123"  # Email password
EMAIL_RECIPIENTS = ["recipient1@example.com", "recipient2@example.com"]  # Recipients of emails

#SEIM settings
#DEFAULT_DIRECTORY = "/home/james/Downloads"  # Default directory to monitor
VIRUSTOTAL_API_KEY_PATH = "/home/API_KEY/api_key.txt"  # Replace
VIRUSTOTAL_API_KEY = ""
# More values for email alerts
RAM_USAGE_THRESHOLD = 90 # Set to None to disable RAM alerts
DISK_USAGE_THRESHOLD = 75 # Set to None to disable disk alerts

DEBUG_MODE = True
