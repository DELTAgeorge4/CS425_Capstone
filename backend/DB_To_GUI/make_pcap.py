from scapy.all import wrpcap
from scapy.layers.l2 import Ether
import Sniffer

packet_list = [row[4] for row in Sniffer.get_packets()]

def convert_packets(packet_list):
    packets = []
    for packet_bytes in packet_list:
        raw_bytes = bytes(packet_bytes)
        try:
            pkt = Ether(raw_bytes)
            packets.append(pkt)
        except:
            continue
    return packets

all_packets = convert_packets(packet_list)

# Write all packets to a .pcap file
wrpcap("full_output.pcap", all_packets)

print(f"Wrote {len(all_packets)} packets to full_output.pcap")
