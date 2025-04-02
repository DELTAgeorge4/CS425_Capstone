# Developed by Nicholas Katsaros

import subprocess
import db_control
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments provided.")
        exit(1)
    if len(sys.argv) > 2:
        print("Too many arguments provided")
        exit(1)

    device = sys.argv[1]
    #device = get_net_device()
    #device = "eth0"

    compilation_command = ["gcc", "-o", "capture_packets", "capture_packets.c", "-lpcap"]

    subprocess.run(compilation_command, text=True)

    packet_capture_command = ["./capture_packets", device]

    process = subprocess.Popen(
        packet_capture_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True 
    )

    line = process.stdout.readline()
    start_message = line.strip()
    print(start_message)

    line = process.stdout.readline()# packet capture length
    line = process.stdout.readline()# packet total length

    while True:
        line = process.stdout.readline()
        if not line:
            continue
        packet = {}
        print(line.strip()) # Should be destination MAC
        packet['destination_mac'] = line.strip()[-17:]

        line = process.stdout.readline()
        print(line.strip()) # Should be source MAC
        packet['source_mac'] = line.strip()[-17:]

        line = process.stdout.readline()
        print(line.strip()) # Should be ethertype
        packet['ethertype'] = line.strip()[-6:]

        line = process.stdout.readline()
        print(line.strip()) # Should be the ethertype meaning
        packet['ethertype_meaning'] = line.strip()[11:]

        process.stdout.readline() # skip a line containing no useful data

        line = process.stdout.readline()
        print(line.strip()) # Should be the raw packet data
        packet['raw_packet'] = line.strip() # Will need to be converted to int array for processing in database

        packet['protocol'] = "Ethernet"

        print(packet)

        db_control.save_packet(packet)
    
