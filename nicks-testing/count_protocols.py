from collections import defaultdict
from scapy.all import *
import db_control

def analyze_packets(packets_list):
    network_protocols = defaultdict(int)
    transport_protocols = defaultdict(int)
    application_protocols = defaultdict(int)
    
    ethertype_map = {0x0800: 'IPv4', 0x86DD: 'IPv6', 0x0806: 'ARP'}
    proto_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
    
    for packet_data in packets_list:
        packet = Ether(bytes(packet_data))
        
        # Network Layer
        if packet.type in ethertype_map:
            network_protocols[ethertype_map[packet.type]] += 1
        else:
            network_protocols[f'Unknown({hex(packet.type)})'] += 1
        
        if IP in packet:
            proto_name = proto_map.get(packet[IP].proto, f'Unknown({packet[IP].proto})')
            transport_protocols[proto_name] += 1
            
            # Transport Layer
            if TCP in packet:
                src_port, dest_port = packet[TCP].sport, packet[TCP].dport
            elif UDP in packet:
                src_port, dest_port = packet[UDP].sport, packet[UDP].dport
            else:
                continue
            
            # Application Layer (Identify based on ports)
            app_protocols = {
                80: 'HTTP', 443: 'HTTPS', 53: 'DNS', 22: 'SSH', 25: 'SMTP',
                110: 'POP3', 143: 'IMAP', 123: 'NTP', 389: 'LDAP', 3306: 'MySQL'
            }
            
            if src_port in app_protocols:
                application_protocols[app_protocols[src_port]] += 1
            elif dest_port in app_protocols:
                application_protocols[app_protocols[dest_port]] += 1
            else:
                application_protocols['Unknown'] += 1
        
    return {
        'network_layer': dict(network_protocols),
        'transport_layer': dict(transport_protocols),
        'application_layer': dict(application_protocols)
    }


def get_protocol_counts(): # give this and next line time parameters later
    packets = db_control.get_packets()
    raw_packet_data = [row[4] for row in packets]
    return analyze_packets(raw_packet_data)

if __name__ == '__main__':
    print(get_protocol_counts())