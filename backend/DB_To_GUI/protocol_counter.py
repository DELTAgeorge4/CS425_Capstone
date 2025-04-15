from collections import defaultdict
from scapy.all import *
import sys
import os

sys.path.append(os.path.dirname(__file__))
import Sniffer

# Manually defining common Ethernet types
ethertype_map = {
    0x0800: 'IPv4', 0x86DD: 'IPv6', 0x0806: 'ARP', 0x8100: 'VLAN', 
    0x8847: 'MPLS', 0x8848: 'MPLS', 0x8863: 'PPPoE Discovery', 
    0x8864: 'PPPoE Session', 0x8906: 'FCoE', 0x9000: 'Loopback'
}

# Common transport-layer protocol mappings (IANA-based)
proto_map = {
    1: 'ICMP', 6: 'TCP', 17: 'UDP', 2: 'IGMP', 8: 'EGP', 89: 'OSPF',
    132: 'SCTP', 46: 'RSVP', 50: 'ESP', 51: 'AH', 136: 'UDPLite'
}

# Comprehensive application-layer protocols by ports (IANA-based)
app_protocols = {
    20: 'FTP-Data', 21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    67: 'DHCP', 68: 'DHCP', 69: 'TFTP', 80: 'HTTP', 110: 'POP3', 119: 'NNTP',
    123: 'NTP', 135: 'MSRPC', 143: 'IMAP', 161: 'SNMP', 389: 'LDAP',
    443: 'HTTPS', 636: 'LDAPS', 993: 'IMAPS', 995: 'POP3S', 3306: 'MySQL',
    3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-Proxy'
}

def analyze_packets(packets_list):
    network_protocols = defaultdict(int)
    transport_protocols = defaultdict(int)
    application_protocols = defaultdict(int)

    for packet_data in packets_list:
        try:
            raw_bytes = bytes(packet_data)  # Convert list of integers to bytes
            packet = Ether(raw_bytes)  # Parse packet
        except Exception:
            continue  # Skip malformed packets

        # Network Layer Recognition
        if packet.haslayer(Ether) and hasattr(packet, "type"):
            network_protocols[ethertype_map.get(packet.type, f'Unknown({hex(packet.type)})')] += 1

        # Transport Layer Recognition
        if packet.haslayer(IP):
            proto_name = proto_map.get(packet[IP].proto, f'Unknown({packet[IP].proto})')
            transport_protocols[proto_name] += 1

            # Application Layer Recognition (Based on Ports)
            if packet.haslayer(TCP):
                src_port, dest_port = packet[TCP].sport, packet[TCP].dport
            elif packet.haslayer(UDP):
                src_port, dest_port = packet[UDP].sport, packet[UDP].dport
            else:
                continue

            if src_port in app_protocols:
                application_protocols[app_protocols[src_port]] += 1
            elif dest_port in app_protocols:
                application_protocols[app_protocols[dest_port]] += 1
            else:
                application_protocols[f'Unknown({src_port}-{dest_port})'] += 1  # Unrecognized port

    return {
        'network_layer': dict(network_protocols),
        'transport_layer': dict(transport_protocols),
        'application_layer': dict(application_protocols)
    }


def get_protocol_counts():
    packets = Sniffer.get_packets()
    raw_packet_data = [row[4] for row in packets]  # Assuming row[4] is a list of integers
    return analyze_packets(raw_packet_data)


if __name__ == '__main__':
    print(get_protocol_counts())
