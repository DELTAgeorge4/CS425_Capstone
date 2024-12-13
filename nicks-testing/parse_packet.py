# Packet info from https://www.geeksforgeeks.org/tcp-ip-packet-format/

def interpret_tcp(packet):
    src_port = packet[0]*255 + packet[1]
    dest_port = packet[2]*255 + packet[3]

    sequence_num = packet[4] * 255 * 255 * 255 + packet[5] * 255 * 255 + packet[6] * 255 + packet[7]
    ack_num = packet[8] * 255 * 255 * 255 + packet[9] * 255 * 255 + packet[10] * 255 + packet[11]

    data_offset = int(packet[12] / 16)


    print("Source Port: " + str(src_port))
    print("Destination Port: " + str(dest_port))
    print("Sequence Number: " + str(sequence_num))
    print("Acknowledgement Number: " + str(data_offset))

if __name__ == "__main__":
    # example IPv4 packet
    raw_data_hex = ["00", "15", "5d", "f8", "51", "88", "00", "15", "5d", "f8", "54", "0e", "08", "00", "45", "00", "00", "3c", "f5", "a4", "40", "00", "6a", "06", "fd", "4f", "0d", "59", "b3", "09", "ac", "1b", "b1", "49", "01", "bb", "b3", "30", "31", "ae", "36", "11", "0c", "a3", "6b", "01", "a0", "12", "ff", "ff", "c6", "e5", "00", "00", "02", "04", "05", "66", "01", "03", "03", "08", "04", "02", "08", "0a", "0f", "e0", "c6", "9b", "41", "08", "b7", "bc"]
    raw_data = []

    for val in raw_data_hex:
        raw_data.append(int(val, 16))
    
    raw_data = raw_data[14:] # Removing ethernet header

    protocol = "Internet Protocol version 4 (IPv4)"

    if protocol == "Internet Protocol version 4 (IPv4)":
        version = int(raw_data[0] / 16) # left nibble
        header_len = raw_data[0] % 16 # right nibble

        header_len_bytes = header_len * 4 # number of bytes in header

        type_of_service = raw_data[1]

        total_len_bytes = raw_data[2]*255 + raw_data[3]

        packet_id = str(raw_data[4]) + str(raw_data[5])

        reserved_bit = raw_data[6] > 127
        do_not_fragment = (raw_data[6] % 128) > 63
        more_fragments = ((raw_data[6] % 128) % 64) > 31

        fragment_offset = (((((raw_data[6] % 128) % 64) % 32) * 255) + raw_data[7]) * 8

        time_to_live = raw_data[8]

        protocol = raw_data[9]

        if protocol == 6:
            protocol_name = "Transmission Control Protocol (TCP)"
        elif protocol == 17:
            protocol_name = "User Datagram Protocol (UDP)"
        else:
            protocol_name = "Unknown"

        header_checksum = raw_data[10]*255 + raw_data[11]

        source_ip = str(raw_data[12]) + "."
        source_ip = source_ip + str(raw_data[13]) + "."
        source_ip = source_ip + str(raw_data[14]) + "."
        source_ip = source_ip + str(raw_data[15])

        dest_ip = str(raw_data[16]) + "."
        dest_ip = dest_ip + str(raw_data[17]) + "."
        dest_ip = dest_ip + str(raw_data[18]) + "."
        dest_ip = dest_ip + str(raw_data[19])

        options = header_len_bytes != 20

        payload = raw_data[20:]


        print("Version: " + str(version))
        print("Header Length: " + str(header_len_bytes))
        print("Type of service: " + str(type_of_service))
        print("Total packet length: " + str(total_len_bytes))
        print("Packet ID: " + str(packet_id))
        print("Reserved bit: " + str(reserved_bit))
        print("Do not fragment? " + str(do_not_fragment))
        print("More fragments? " + str(more_fragments))
        print("Fragment offset: " + str(fragment_offset))
        print("Time to live: " + str(time_to_live))
        print("Protocol value: " + str(protocol))
        print("Protocol name: " + protocol_name)
        print("Checksum: " + str(header_checksum))
        print("Source IP: " + source_ip)
        print("Dest IP: " + dest_ip)
        print("Options? " + str(options))

        print("Payload: " + str(payload))

        if protocol == 6:
            interpret_tcp(payload)
