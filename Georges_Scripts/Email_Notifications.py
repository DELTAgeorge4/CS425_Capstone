import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from psycopg2 import sql
from datetime import datetime
import config
import time

# Database connection details
DB_HOST = config.DB_HOST
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD

# Email configuration
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
EMAIL_USER = config.EMAIL_USER
EMAIL_PASSWORD = config.EMAIL_PASSWORD
RECIPIENTS = config.EMAIL_RECIPIENTS

# Global thresholds for RAM and disk usage alerts
RAM_USAGE_THRESHOLD = config.RAM_USAGE_THRESHOLD
DISK_USAGE_THRESHOLD = config.DISK_USAGE_THRESHOLD

# Enable or disable Suricata and Honeypot alerts
ENABLE_SURICATA_ALERTS = config.ENABLE_SURICATA_ALERTS
ENABLE_HONEYPOT_ALERTS = config.ENABLE_HONEYPOT_ALERTS

# Global variables to track the last processed IDs
last_suricata_id = 0
last_honeypot_id = 0

# Polling interval in seconds
POLL_INTERVAL = 60  # Check for new rows every 60 seconds

def send_email_alert(subject, body):
    """Send an email notification with the given subject and body."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ", ".join(RECIPIENTS)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, RECIPIENTS, msg.as_string())
        print(f"Alert email sent: {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")

def fetch_high_usage(metric, threshold):
    """Fetch rows where a specified metric exceeds the threshold."""
    if threshold is None:
        return []  # Alerts are disabled for this metric

    try:
        with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                query = sql.SQL(f"""
                    SELECT hostname, {metric}, timestamp
                    FROM snmp_metrics
                    WHERE {metric} > %s
                """)
                cur.execute(query, (threshold,))
                return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def process_snmp_alerts():
    """Check and send alerts for high RAM and Disk usage."""
    # Check for high RAM usage
    if RAM_USAGE_THRESHOLD is not None:
        ram_rows = fetch_high_usage("ram_percent_used", RAM_USAGE_THRESHOLD)
        for row in ram_rows:
            hostname, usage, timestamp = row
            subject = f"High RAM Usage Alert: {hostname}"
            body = (
                f"Alert! The following host has high RAM usage:\n\n"
                f"Hostname: {hostname}\n"
                f"RAM Usage: {usage}%\n"
                f"Timestamp: {timestamp}\n"
            )
            send_email_alert(subject, body)

    # Check for high Disk usage
    if DISK_USAGE_THRESHOLD is not None:
        disk_rows = fetch_high_usage("root_dir_percent_used", DISK_USAGE_THRESHOLD)
        for row in disk_rows:
            hostname, usage, timestamp = row
            subject = f"High Disk Usage Alert: {hostname}"
            body = (
                f"Alert! The following host has high Disk usage:\n\n"
                f"Hostname: {hostname}\n"
                f"Disk Usage: {usage}%\n"
                f"Timestamp: {timestamp}\n"
            )
            send_email_alert(subject, body)

def fetch_new_rows(table, id_column, last_id):
    """Fetch new rows added to a table since the last ID."""
    try:
        with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                query = sql.SQL(f"SELECT * FROM {table} WHERE {id_column} > %s")
                cur.execute(query, (last_id,))
                return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error while fetching from {table}: {e}")
        return []

def process_suricata_alerts():
    """Check for new rows in the Suricata table and send alerts."""
    global last_suricata_id
    rows = fetch_new_rows("suricata", "id", last_suricata_id)
    for row in rows:
        row_id, timestamp, source_ip, source_port, dest_ip, dest_port, protocol, alert_message = row
        subject = f"New Suricata Alert: {alert_message}"
        body = (
            f"A new Suricata alert has been generated:\n\n"
            f"Timestamp: {timestamp}\n"
            f"Source: {source_ip}:{source_port}\n"
            f"Destination: {dest_ip}:{dest_port}\n"
            f"Protocol: {protocol}\n"
            f"Alert Message: {alert_message}\n"
        )
        send_email_alert(subject, body)
        last_suricata_id = max(last_suricata_id, row_id)

def process_honeypot_alerts():
    """Check for new rows in the Honeypot table and send alerts."""
    global last_honeypot_id
    rows = fetch_new_rows("honeypot", "id", last_honeypot_id)
    for row in rows:
        row_id, timestamp, alert_type, src_ip, dst_ip, port = row
        subject = f"New Honeypot Alert: {alert_type}"
        body = (
            f"A new Honeypot alert has been generated:\n\n"
            f"Timestamp: {timestamp}\n"
            f"Alert Type: {alert_type}\n"
            f"Source IP: {src_ip}\n"
            f"Destination IP: {dst_ip}\n"
            f"Port: {port}\n"
        )
        send_email_alert(subject, body)
        last_honeypot_id = max(last_honeypot_id, row_id)

def main():
    """Main loop to continuously process alerts."""
    while True:
        # Process SNMP alerts
        if RAM_USAGE_THRESHOLD is not None or DISK_USAGE_THRESHOLD is not None:
            process_snmp_alerts()

        # Process Suricata alerts
        if ENABLE_SURICATA_ALERTS:
            process_suricata_alerts()

        # Process Honeypot alerts
        if ENABLE_HONEYPOT_ALERTS:
            process_honeypot_alerts()

        if all([
            RAM_USAGE_THRESHOLD is None,
            DISK_USAGE_THRESHOLD is None,
            not ENABLE_SURICATA_ALERTS,
            not ENABLE_HONEYPOT_ALERTS
        ]):
            print("All alerts are disabled. No checks performed.")

        # Sleep before the next check
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted. Exiting...")
