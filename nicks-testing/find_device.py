import subprocess

def read_until_input_needed(process):
    output = []
    while True:
        line = process.stdout.readline()
        if not line:
            break
    
        output.append(line.strip())
        print(line.strip())

    print("Escaped loop")
    return output


if __name__ == "__main__":
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
    device_info = read_until_input_needed(process)

    devices = []
    for row in device_info:
        if "Device name" in row:
            devices.append(row.split(":")[-1].strip())
    
    exit_code = process.wait()

    print("Exit code: " + str(exit_code))
    if(exit_code == 0):
        print("Process terminated succesfully")
    else:
        print("Error encountered. Process is still running")
        print("Process is being forcibly terminated")
        process.terminate()