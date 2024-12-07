#!/usr/bin/env python3
import json
import psycopg2
from psycopg2 import sql

# Database connection details
DB_HOST = "localhost"
DB_NAME = "nss"
DB_USER = "postgres"
DB_PASSWORD = "password123"

# Path to Suricata logs
#SURICATA_LOG_FILE = "/var/log/suricata/eve.json"
SURICATA_LOG_FILE = "/home/CS425_Capstone/Georges_Scripts/Suricata/Suricata_Logs/suricata_ix1.10027422/eve.json"

def connect_db():
    """Connect to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Exception as e:
        print("Error connecting to the database:", e)
        exit(1)

def insert_log(cursor, log_data):
    """Insert a parsed log entry into the database."""
    query = sql.SQL("""
        INSERT INTO suricata (timestamp, source_ip, source_port, dest_ip, dest_port, protocol, alert_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """)
    cursor.execute(query, (
        log_data.get("timestamp"),
        log_data.get("src_ip"),
        log_data.get("src_port"),
        log_data.get("dest_ip"),
        log_data.get("dest_port"),
        log_data.get("proto"),
        log_data.get("alert", {}).get("signature")
    ))

def parse_logs():
    """Read and parse Suricata logs."""
    connection = connect_db()
    cursor = connection.cursor()

    try:
        with open(SURICATA_LOG_FILE, "r") as log_file:
            for line in log_file:
                log_entry = json.loads(line)

                # Parse only alert events
                if log_entry.get("event_type") == "alert":
                    insert_log(cursor, log_entry)

        connection.commit()
        print("Logs successfully stored in the database.")
    except Exception as e:
        print("Error processing logs:", e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    parse_logs()
