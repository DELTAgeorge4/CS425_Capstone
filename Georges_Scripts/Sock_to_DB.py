#!/usr/bin/env python3
import socket
import json
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="suricata_alerts",
    user="your_pg_user",
    password="your_pg_password",
    host="localhost"
)
cursor = conn.cursor()

# Connect to the Unix socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect("/var/run/suricata/eve.sock")

while True:
    data = sock.recv(4096)
    if not data:
        break
    try:
        alert = json.loads(data.decode('utf-8'))
        cursor.execute("INSERT INTO alerts (alert) VALUES (%s)", [json.dumps(alert)])
        conn.commit()
    except json.JSONDecodeError:
        continue

cursor.close()
conn.close()




#with open('/var/log/suricata/eve.json') as f:
#    for line in f:
#        data = json.loads(line)
#        cursor.execute(
#            "INSERT INTO your_table_name (field1, field2) VALUES (%s, %s)",
#            (data['field1'], data['field2'])
#        )
#conn.commit()
#conn.close()
