import subprocess
import db_control

def read_until_input_needed(process):
    output = []
    while True:
        line = process.stdout.readline()
        if "Enter the number for the device you would like to get information about:" in line:
            output.append(line.strip())
            print(line.strip())
            break
    
        output.append(line.strip())
        print(line.strip())
    print("Escaped loop")
    return output


def get_net_device():
    compilation_command = ["gcc", "-o", "find_device", "find_device.c", "-lpcap"]

    subprocess.run(compilation_command, text=True)
    
    device_finder_path = "./find_device"

    process = subprocess.Popen(
        device_finder_path,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True 
    )
    print("program running")
    read_until_input_needed(process)


    choice = input()

    process.stdin.write(choice + '\n')
    process.stdin.flush()

    line = process.stdout.readline()
    device_name = line.strip()
    print(line.strip())

    for i in range(3):
        line = process.stdout.readline()
        print(line.strip())

    exit_code = process.wait()

    print("Exit code: " + str(exit_code))
    if(exit_code == 0):
        print("Process terminated succesfully")
    else:
        print("Error encountered. Process is still running")
        print("Process is being forcibly terminated")
        process.terminate()
        process.wait()

    return device_name


if __name__ == "__main__":
    #device = get_net_device()
    device = "eth0"

    compilation_command = ["gcc", "-o", "capture_packets", "capture_packets.c", "-lpcap"]

    subprocess.run(compilation_command, text=True)

    packet_capture_command = ["sudo", "./capture_packets", device]

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

    for i in range(10): # 10 is arbitrary, this should eventually be an infinite loop
        packet = {}
        line = process.stdout.readline()
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
    





    

    


    

    
    
