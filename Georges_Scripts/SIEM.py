#!/usr/bin/env python3
import json
import logging
from datetime import datetime, timedelta
import requests
import psycopg2
from psycopg2 import sql
import config  # Make sure this file provides DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, AGENT_BASE_URL

# --- Database Functions ---

def connect_db():
    try:
        connection = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        return connection
    except Exception as e:
        logging.error("Error connecting to the database: %s", e)
        exit(1)

def insert_siem_log(cursor, log_data):
    query = """
        INSERT INTO siem_logs (timestamp, source, event_type, severity, message, agent_info)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        log_data.get("timestamp"),
        log_data.get("source"),
        log_data.get("event_type"),
        log_data.get("severity"),
        log_data.get("message"),
        json.dumps(log_data)  # Save the full log as JSON for additional context
    ))

# --- SIEM Components ---

class LogCollector:
    """
    Collects logs from various sources.
    """
    def __init__(self):
        self.logs = []

    def collect_log(self, log_data):
        self.logs.append(log_data)

    def get_logs(self):
        return self.logs

class Normalizer:
    """
    Normalizes raw logs into a standard schema.
    """
    @staticmethod
    def normalize(raw_log):
        normalized_log = {
            "timestamp": raw_log.get("timestamp", datetime.utcnow().isoformat()),
            "source": raw_log.get("source", "unknown"),
            "event_type": raw_log.get("event_type", "unknown"),
            "severity": raw_log.get("severity", "low"),
            "message": raw_log.get("message", ""),
        }
        return normalized_log

class CorrelationEngine:
    """
    Applies basic rule-based correlation.
    """
    def __init__(self, threshold=3, window_seconds=30):
        self.threshold = threshold
        self.window_seconds = window_seconds

    def correlate(self, normalized_logs):
        alerts = []
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Count high-severity events within the time window.
        high_severity_logs = [
            log for log in normalized_logs
            if log.get("severity") == "high" and datetime.fromisoformat(log.get("timestamp")) >= window_start
        ]
        if len(high_severity_logs) >= self.threshold:
            alerts.append({
                "alert": "High number of high-severity events",
                "count": len(high_severity_logs),
                "time_window": self.window_seconds,
                "timestamp": now.isoformat()
            })
        return alerts

class AlertManager:
    """
    Manages alert notifications.
    """
    def send_alerts(self, alerts):
        for alert in alerts:
            logging.warning("SIEM Alert: %s", alert)
            # Extend this method to send email/SMS notifications if desired.

class AgentConnector:
    """
    Connects to a remote agent via REST API.
    The agent endpoint should be cross-platform (Linux and Windows) and expose /api/logs.
    """
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def fetch_logs(self):
        try:
            response = requests.get(f"{self.base_url}/api/logs")
            response.raise_for_status()
            logs = response.json()
            logging.info("Fetched %d logs from remote agent.", len(logs))
            return logs
        except Exception as e:
            logging.error("Error fetching logs from agent: %s", e)
            return []

# --- Main SIEM Execution ---

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Initialize SIEM components
    collector = LogCollector()
    correlation_engine = CorrelationEngine(threshold=3, window_seconds=30)
    alert_manager = AlertManager()
    agent_connector = AgentConnector(base_url=config.AGENT_BASE_URL)

    # 1. Fetch logs from the remote agent.
    agent_logs = agent_connector.fetch_logs()
    for log in agent_logs:
        # Mark the source as "agent" to distinguish these logs.
        log["source"] = "agent"
        collector.collect_log(log)

    # 2. Simulate internal NSS logs (e.g., Suricata, honeypot, SNMP)
    sample_logs = [
        {"timestamp": datetime.utcnow().isoformat(), "source": "suricata", "event_type": "alert", "severity": "high", "message": "Potential intrusion detected."},
        {"timestamp": datetime.utcnow().isoformat(), "source": "honeypot", "event_type": "alert", "severity": "high", "message": "Suspicious activity from external IP."},
        {"timestamp": datetime.utcnow().isoformat(), "source": "snmp", "event_type": "status", "severity": "low", "message": "SNMP agent started."},
        {"timestamp": datetime.utcnow().isoformat(), "source": "suricata", "event_type": "alert", "severity": "high", "message": "Malicious payload detected."},
    ]
    for log in sample_logs:
        collector.collect_log(log)

    # 3. Normalize collected logs.
    normalized_logs = [Normalizer.normalize(log) for log in collector.get_logs()]

    # 4. Insert normalized logs into the PostgreSQL database.
    conn = connect_db()
    cursor = conn.cursor()
    for norm_log in normalized_logs:
        try:
            insert_siem_log(cursor, norm_log)
        except Exception as e:
            logging.error("Error inserting log: %s", e)
    conn.commit()
    cursor.close()
    conn.close()

    # 5. Correlate logs and handle alerts.
    alerts = correlation_engine.correlate(normalized_logs)
    alert_manager.send_alerts(alerts)

if __name__ == "__main__":
    main()
