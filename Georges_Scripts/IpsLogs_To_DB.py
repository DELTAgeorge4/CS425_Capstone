#!/usr/bin/env python3
import json
import psycopg2
from psycopg2 import sql
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import config
import time

# Database connection details
DB_HOST = config.DB_HOST
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD

# Path to Suricata log file
SURICATA_LOG_FILE = config.SURICATA_LOG_FILE

# Connect to the PostgreSQL database
def connect_db():
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

# Insert a parsed log entry into the database, avoiding duplicates
def insert_log(cursor, log_data):
    query = sql.SQL("""
        INSERT INTO suricata (timestamp, source_ip, source_port, dest_ip, dest_port, protocol, alert_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp, source_ip, source_port, dest_ip, dest_port, protocol, alert_message) DO NOTHING
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

# Process a single log file line
def process_log_line(connection, line):
    cursor = connection.cursor()
    try:
        log_entry = json.loads(line)
        if log_entry.get("event_type") == "alert":
            insert_log(cursor, log_entry)
        connection.commit()
    except Exception as e:
        print(f"Error processing log line: {e}")
        connection.rollback()
    finally:
        cursor.close()

# Event handler for file changes
class LogHandler(FileSystemEventHandler):
    def __init__(self, connection):
        self.connection = connection

    def on_modified(self, event):
        if event.src_path == SURICATA_LOG_FILE:
            try:
                with open(SURICATA_LOG_FILE, "r") as log_file:
                    for line in log_file:
                        process_log_line(self.connection, line)
            except Exception as e:
                print(f"Error reading log file: {e}")

if __name__ == "__main__":
    connection = connect_db()
    event_handler = LogHandler(connection)
    observer = Observer()
    observer.schedule(event_handler, path=SURICATA_LOG_FILE, recursive=False)
    
    try:
        observer.start()
        print("Monitoring started.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        connection.close()