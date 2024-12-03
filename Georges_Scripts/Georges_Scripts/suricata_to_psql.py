import json
import psycopg2
from psycopg2.extras import Json

# Database connection
conn = psycopg2.connect(
    dbname="suricata",
    user="suricata_user",
    password="password",
    host="localhost"
)
cur = conn.cursor()

# Path to the Suricata eve.json file
log_file = "/var/log/eve.json"

def process_log_line(line):
    try:
        data = json.loads(line)
        timestamp = data.get("timestamp")
        src_ip = data.get("src_ip")
        src_port = data.get("src_port")
        dest_ip = data.get("dest_ip")
        dest_port = data.get("dest_port")
        protocol = data.get("proto")
        alert = data.get("alert", {}).get("signature")
        raw = data  # Store the full JSON as a fallback

        # Insert into database
        cur.execute("""
            INSERT INTO logs (timestamp, src_ip, src_port, dest_ip, dest_port, protocol, alert, raw)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (timestamp, src_ip, src_port, dest_ip, dest_port, protocol, alert, Json(raw)))

        conn.commit()
    except Exception as e:
        print(f"Error processing line: {e}")

# Tail the eve.json log file
with open(log_file, 'r') as f:
    for line in f:
        process_log_line(line)

cur.close()
conn.close()
