import socket
from scapy.all import sniff
import threading
import psycopg2
from datetime import datetime

# Configuration
TARGET_IP = "192.168.1.100"  # Replace with the target IP address you want to monitor
PORTS = [80, 443, 3389]  # Ports to listen on and monitor

# PostgreSQL connection details
DB_HOST = "localhost"
DB_NAME = "honeypot_db"
DB_USER = "honeypot_user"
DB_PASSWORD = "password"

def log_to_database(alert_type, src_ip, dst_ip, port):
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        timestamp = datetime.now()
        cursor.execute(
            """
            INSERT INTO honeypot (timestamp, alert_type, src_ip, dst_ip, port)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (timestamp, alert_type, src_ip, dst_ip, port)
        )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Failed to log to database: {e}")

def monitor_traffic(target_ip, ports):
    def packet_callback(packet):
        if packet.haslayer('IP') and packet['IP'].dst == target_ip:
            if packet.haslayer('TCP') and packet['TCP'].dport in ports:
                src_ip = packet['IP'].src
                dst_ip = packet['IP'].dst
                port = packet['TCP'].dport
                log_to_database("Traffic Detected", src_ip, dst_ip, port)

    sniff(filter=f"tcp and dst {target_ip}", prn=packet_callback)

def create_honeypot_listener(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen(5)
    print(f"Listening for connections on port {port}...")
    
    while True:
        client_socket, addr = server_socket.accept()
        log_to_database("Connection Attempt", addr[0], TARGET_IP, port)
        client_socket.close()

def main():
    # Start packet monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_traffic, args=(TARGET_IP, PORTS))
    monitor_thread.daemon = True
    monitor_thread.start()

    # Create honeypot listeners for specified ports
    listener_threads = []
    for port in PORTS:
        listener_thread = threading.Thread(target=create_honeypot_listener, args=(port,))
        listener_thread.daemon = True
        listener_thread.start()
        listener_threads.append(listener_thread)
    
    # Keep the main thread running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down honeypot...")

if __name__ == "__main__":
    main()
