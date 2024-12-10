import psycopg2
from psycopg2 import sql
import getpass

def main():
    # Prompt the user for the `postgres` user password
    postgres_password = getpass.getpass("Enter the password for the PostgreSQL 'postgres' user: ")

    # Database connection parameters
    db_params = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': postgres_password,
        'host': 'localhost',
        'port': 5432
    }

    try:
        # Connect to the default PostgreSQL database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True  # Enable auto-commit for creating the database
        cursor = conn.cursor()

        # Create the `nss` database
        print("Creating database 'nss'...")
        cursor.execute("DROP DATABASE IF EXISTS nss;")
        cursor.execute("CREATE DATABASE nss;")

        # Close connection to default database
        cursor.close()
        conn.close()

        # Connect to the `nss` database
        db_params['dbname'] = 'nss'
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Create tables in the `nss` database
        print("Creating tables...")
        honeypot_table = """
        CREATE TABLE IF NOT EXISTS honeypot (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            alert_type VARCHAR(255) NOT NULL,
            src_ip INET NOT NULL,
            dst_ip INET NOT NULL,
            port INT NOT NULL
        );
        """
        suricata_table = """
        CREATE TABLE IF NOT EXISTS suricata (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            source_ip INET NOT NULL,
            source_port INT NOT NULL,
            dest_ip INET NOT NULL,
            dest_port INT NOT NULL,
            protocol VARCHAR(50) NOT NULL,
            alert_message TEXT NOT NULL,
            UNIQUE (timestamp, source_ip, source_port, dest_ip, dest_port, protocol, alert_message)
        );
        """
        snmp_metrics_table = """
        CREATE TABLE IF NOT EXISTS snmp_metrics (
            id SERIAL PRIMARY KEY,
            hostname VARCHAR(255),
            system_uptime DOUBLE PRECISION,
            cpu_usage DOUBLE PRECISION,
            ram_used DOUBLE PRECISION,
            ram_total DOUBLE PRECISION,
            ram_percent_used DOUBLE PRECISION,
            root_dir_used_storage DOUBLE PRECISION,
            root_dir_total_storage DOUBLE PRECISION,
            root_dir_percent_used DOUBLE PRECISION,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        # Execute table creation queries
        cursor.execute(honeypot_table)
        cursor.execute(suricata_table)
        cursor.execute(snmp_metrics_table)

        print("Tables created successfully.")

        # Commit the changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print("An error occurred while working with PostgreSQL:")
        print(e)
    finally:
        if conn:
            conn.close()
        print("Setup complete.")

if __name__ == "__main__":
    main()
