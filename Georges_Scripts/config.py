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



DEBUG_MODE = True
