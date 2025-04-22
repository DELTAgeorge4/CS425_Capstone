# config.py

import os
import json
from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Suricata Log File
    SURICATA_LOG_FILE: str = "/home/CS425_Capstone/Georges_Scripts/Suricata/Suricata_Logs/eve.json"

    # Topology Configuration
    TOPOLOGY_HOSTS: List[str] = ['192.168.14.1']  # Router/switch IP(s)
    TOPOLOGY_COMMUNITY: str = 'public'
    TOPOLOGY_SNMP_VERSION: int = 1  # 0 for v1, 1 for v2c

    # Honeypot Configuration
    HONEYPOT_TARGET_IPS: str = "192.168.14.14"
    HONEYPOT_TARGET_PORTS: List[int] = [443, 8080, 223]

    # SNMP Clients Configuration
    SNMP_HOSTS: List[str] = ["192.168.14.14", "192.168.14.11"]
    SNMP_WORKERS: int = 4

    # Testing Tables
    TESTING_TABLES: List[str] = ["snmp_metrics", "suricata", "honeypot"]

    # Database Configuration (using plain string for password)
    DB_HOST: str = "localhost"
    DB_NAME: str = "nss"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password123"  # Plain string password

    # SNMP Email Alert Settings (using plain string for password)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USER: str = "your_email@example.com"
    EMAIL_PASSWORD: str = "your_email_password"  # Plain string password
    EMAIL_RECIPIENTS: List[str] = ["recipient1@example.com", "recipient2@example.com"]

    # Email Alert Thresholds
    RAM_USAGE_THRESHOLD: Optional[int] = 90
    DISK_USAGE_THRESHOLD: Optional[int] = 75

    # Debug Mode
    DEBUG_MODE: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create the settings instance
settings: Settings = Settings()


def load_config_file(filepath: str) -> None:
    """
    Load configuration values from a JSON file and update the settings instance.
    """
    global settings
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            config_data = json.load(f)
            settings = Settings(**config_data)
    else:
        raise FileNotFoundError(f"Config file '{filepath}' not found.")


def load_default_config() -> None:
    """
    Reload the default configuration values.
    """
    global settings
    settings = Settings()


# Module-level __getattr__ to forward attribute accesses to the settings instance.
def __getattr__(name: str):
    try:
        return getattr(settings, name)
    except AttributeError as exc:
        raise AttributeError(f"module {__name__} has no attribute {name}") from exc
