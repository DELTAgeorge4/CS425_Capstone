import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from psycopg2 import sql
import config

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

def fetch_high_usage(metric, threshold):
    """
    Fetch rows where a specified metric (e.g., RAM or disk usage) exceeds the threshold.
    """
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

def send_email_alert(hostname, metric, usage, timestamp):
    """
    Send an email notification for high resource usage.
    """
    try:
        subject = f"High {metric.capitalize()} Usage Alert: {hostname}"
        body = (
            f"Alert! The following host has high {metric} usage:\n\n"
            f"Hostname: {hostname}\n"
            f"{metric.capitalize()} Usage: {usage}%\n"
            f"Timestamp: {timestamp}\n\n"
            f"Please take appropriate action."
        )
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ", ".join(RECIPIENTS)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, RECIPIENTS, msg.as_string())
        print(f"Alert email sent for {hostname} ({metric.capitalize()}: {usage}%).")

    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    """
    Main function to check and send alerts for high RAM and disk usage.
    """
    # Check for high RAM usage
    if RAM_USAGE_THRESHOLD is not None:
        ram_rows = fetch_high_usage("ram_percent_used", RAM_USAGE_THRESHOLD)
        for row in ram_rows:
            hostname, usage, timestamp = row
            send_email_alert(hostname, "RAM", usage, timestamp)

    # Check for high disk usage
    if DISK_USAGE_THRESHOLD is not None:
        disk_rows = fetch_high_usage("root_dir_percent_used", DISK_USAGE_THRESHOLD)
        for row in disk_rows:
            hostname, usage, timestamp = row
            send_email_alert(hostname, "Disk", usage, timestamp)

    if RAM_USAGE_THRESHOLD is None and DISK_USAGE_THRESHOLD is None:
        print("All alerts are disabled. No checks performed.")

if __name__ == "__main__":
    main()
