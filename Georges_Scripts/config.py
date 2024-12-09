# config.py

# Change to path where .json logs get placed from suricata, typically /ver/logs/suricata/eve.json
SURICATA_LOG_FILE = "/home/CS425_Capstone/Georges_Scripts/Suricata/Suricata_Logs/eve.json"

# Honeypot config
HONEYPOT_TARGET_IPS = "192.168.14.14"
HONEYPOT_TARGET_PORTS = [443, 8080]

# SNMP Clients formatable via 192.168.1.1 or 192.168.1.1/24
SNMP_HOSTS = ["192.168.14.14", "192.168.14.11"]

# Secify the amount of threads you want snmp to use.
SNMP_WORKERS = 4

# Define tables you want to incude in INTERACT_W_TABLES.PY script
TESTING_TABLES = ["snmp_metrics", "suricata", "honeypot"]

# Preconfigured Database Info, SHOULD NOT TOUCH UNLESS MANUALLY CHANGED
DB_HOST = "localhost"
DB_NAME = "nss"
DB_USER = "postgres"
DB_PASSWORD = "password123"

# SNMP Settings for email alerts
SMTP_SERVER = "smtp.gmail.com"  # Use email SMTP server
SMTP_PORT = 587
EMAIL_USER = "your_email@example.com"  # Your email address
EMAIL_PASSWORD = "your_email_password"  # Email password
EMAIL_RECIPIENTS = ["recipient1@example.com", "recipient2@example.com"]  # Recipients of emails

# More values for email alerts
RAM_USAGE_THRESHOLD = 90 # Set to None to disable RAM alerts
DISK_USAGE_THRESHOLD = 75 # Set to None to disable disk alerts

DEBUG_MODE = True
