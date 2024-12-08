# config.py

# Change to path where .json logs get placed from suricata, typically /ver/logs/suricata/eve.json
SURICATA_LOG_FILE = "/home/CS425_Capstone/Georges_Scripts/Suricata/Suricata_Logs/suricata_ix1.10027422/eve.json"

# Honeypot config
HONEYPOT_TARGET_IPS = "192.168.14.14"
HONEYPOT_TARGET_PORTS = [443, 8080]

# SNMP Clients
SNMP_HOSTS = ["192.168.14.14", "192.168.14.11"]

# Secify the amount of threads you want snmp to use.
SNMP_WORKERS = 25

# Preconfigured Database Info, SHOULD NOT TOUCH UNLESS MANUALLY CHANGED
DB_HOST = "localhost"
DB_NAME = "nss"
DB_USER = "postgres"
DB_PASSWORD = "password123"



DEBUG_MODE = True
