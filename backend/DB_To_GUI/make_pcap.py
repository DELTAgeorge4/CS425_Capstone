import argparse
from datetime import datetime
from scapy.all import wrpcap, Ether
import Sniffer

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=str, default=None)
parser.add_argument("--end", type=str, default=None)
args = parser.parse_args()

start_time = datetime.fromisoformat(args.start) if args.start else datetime.min
end_time = datetime.fromisoformat(args.end) if args.end else datetime.max

packet_list = [row[4] for row in Sniffer.get_packets(start_time=start_time, end_time=end_time)]

def convert_packets(packet_list):
    packets = []
    for packet_bytes in packet_list:
        try:
            pkt = Ether(bytes(packet_bytes))
            packets.append(pkt)
        except:
            continue
    return packets

all_packets = convert_packets(packet_list)

wrpcap("full_output.pcap", all_packets)

print(f"Wrote {len(all_packets)} packets to full_output.pcap")
