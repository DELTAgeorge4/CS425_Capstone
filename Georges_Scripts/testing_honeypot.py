import socket
from scapy.all import sniff
import threading

TARGET_IP = "192.168.14.14" # So far only works if attacher uses ip of the localhost
PORTS = [443, 8080]

def monitor_traffic(target_ip, ports):
    def packet_callback(packet):
        if packet.haslayer('IP') and packet['IP'].dst == target_ip:
            if packet.haslayer('TCP') and packet['TCP'].dport in ports:
                print(f"Traffic detected: {packet['IP'].src} -> {packet['IP'].dst}:{packet['TCP'].dport}")

    sniff(filter=f"tcp and dst {target_ip}", prn=packet_callback)

def create_honeypot_listener(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TARGET_IP, port))
    server_socket.listen(5)
    print(f"Listening for connections on port {port}...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection attempt detected from {addr} on port {port}")
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
