from scapy.all import sniff
from datetime import datetime

def log_packet(packet):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] Packet captured:")
    packet.show()

def main():
    print("Sniffing packets on eth0... Press Ctrl+C to stop.")
    sniff(iface="eth0", prn=log_packet, store=False)

if __name__ == "__main__":
    main()
