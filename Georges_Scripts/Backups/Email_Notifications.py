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

def fetch_high_ram_usage():
    """Fetch rows where RAM percentage used exceeds 90%."""
    try:
        with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT hostname, ram_percent_used, timestamp
                    FROM snmp_metrics
                    WHERE ram_percent_used > 90
                """)
                cur.execute(query)
                return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def send_email_alert(hostname, ram_percent_used, timestamp):
    """Send an email notification for high RAM usage."""
    try:
        subject = f"High RAM Usage Alert: {hostname}"
        body = (
            f"Alert! The following host has high RAM usage:\n\n"
            f"Hostname: {hostname}\n"
            f"RAM Usage: {ram_percent_used}%\n"
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
        print(f"Alert email sent for {hostname}.")

    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    """Main function to check and send alerts."""
    rows = fetch_high_ram_usage()
    if rows:
        for row in rows:
            hostname, ram_percent_used, timestamp = row
            send_email_alert(hostname, ram_percent_used, timestamp)
    else:
        print("No hosts with high RAM usage found.")

if __name__ == "__main__":
    main()
