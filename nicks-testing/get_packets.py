# Developed by Nicholas Katsaros
import db_control
import sys


if __name__ == "__main__":
    if len(sys.argv) > 4:
        print("Too many arguments provided")
        exit(1)
    elif len(sys.argv) < 4:
        print("Too few arguments provided")
        exit(1)

    start_time = sys.argv[1]
    end_time = sys.argv[2]
    network_packet_type = sys.argv[3]

    if start_time == 'None':
        if end_time == 'None':
            packets = db_control.get_packets()
        else:
            packets = db_control.get_packets(end_time=end_time)
    else:
        if end_time == 'None':
            packets = db_control.get_packets(start_time=start_time)
        else:
            packets = db_control.get_packets(start_time=start_time, end_time=end_time)


    for row in packets:
        print("Link Layer Type: " + row[0])
        print("Destination MAC address: " + row[1])
        print("Source MAC address: " + row[2])
        print("Network Layer Packet Type: " + row[3])
        print("Raw packet data(in decimal): " + str(row[4]))
        print("Time recorded: " + str(row[5]) + '\n')