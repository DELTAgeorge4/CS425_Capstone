from scapy.all import Ether, IP, TCP, UDP, Raw

def analyze_packet(byte_list):
    # Convert list of ints to bytes
    raw_bytes = bytes(byte_list)
    
    try:
        pkt = Ether(raw_bytes)
    except Exception as e:
        print("Failed to parse packet:", e)
        return

    print("\n--- Packet Protocol Analysis ---")

    # Layer 2 - Ethernet
    if pkt.haslayer(Ether):
        print("L2: Ethernet")

    # Layer 3 - IP
    if pkt.haslayer(IP):
        print("L3: IPv4")
        ip_layer = pkt[IP]
        print(f"    Source IP: {ip_layer.src}")
        print(f"    Dest IP:   {ip_layer.dst}")
    else:
        print("L3: Not IPv4")

    # Layer 4 - TCP/UDP
    if pkt.haslayer(TCP):
        tcp_layer = pkt[TCP]
        print("L4: TCP")
        print(f"    Source Port: {tcp_layer.sport}")
        print(f"    Dest Port:   {tcp_layer.dport}")
    elif pkt.haslayer(UDP):
        udp_layer = pkt[UDP]
        print("L4: UDP")
        print(f"    Source Port: {udp_layer.sport}")
        print(f"    Dest Port:   {udp_layer.dport}")
    else:
        print("L4: Not TCP/UDP")

    # Layer 7 - Application guess
    if pkt.haslayer(Raw):
        l7_guess = "Unknown"
        if pkt.haslayer(TCP):
            dport = pkt[TCP].dport
            if dport == 80 or dport == 8080:
                l7_guess = "HTTP"
            elif dport == 443:
                l7_guess = "HTTPS"
            elif dport == 22:
                l7_guess = "SSH"
            elif dport == 53:
                l7_guess = "DNS"
        elif pkt.haslayer(UDP):
            dport = pkt[UDP].dport
            if dport == 53:
                l7_guess = "DNS"
            elif dport == 123:
                l7_guess = "NTP"

        print(f"L7: Possibly {l7_guess} (based on port {dport})")
    else:
        print("L7: No application data")

# Example usage
if __name__ == "__main__":
    packet = [156, 5, 214, 56, 60, 202, 188, 36, 17, 153, 14, 247, 8, 0, 69, 8, 0, 140, 136, 79, 64, 0, 64, 6, 1, 104, 192, 168, 14, 14, 143, 170, 82, 76, 0, 22, 191, 107, 207, 230, 118, 103, 91, 62, 142, 70, 80, 24, 25, 79, 177, 43, 0, 0, 205, 253, 112, 0, 27, 34, 251, 215, 64, 100, 91, 192, 29, 92, 232, 28, 16, 69, 91, 175, 160, 74, 85, 254, 156, 128, 235, 219, 177, 188, 60, 238, 142, 94, 219, 153, 68, 222, 40, 206, 28, 165, 223, 145, 29, 103, 40, 176, 187, 171, 81, 71, 43, 73, 141, 190, 242, 151, 207, 88, 166, 67, 85, 17, 155, 151, 61, 44, 141, 52, 113, 72, 33, 86, 24, 87, 213, 51, 133, 177, 168, 73, 216, 234, 87, 0, 165, 74, 84, 29, 155, 130, 29, 52, 181, 48, 29, 244, 185, 238]
    analyze_packet(packet)
