import db_control


if __name__ == "__main__":
    packets = db_control.get_packets()

    for row in packets:
        print("Link Layer Type: " + row[0])
        print("Destination MAC address: " + row[1])
        print("Source MAC address: " + row[2])
        print("Network Layer Packet Type: " + row[3])
        print("Raw packet data(in decimal): " + str(row[4]))
        print("Time recorded: " + str(row[5]) + '\n')