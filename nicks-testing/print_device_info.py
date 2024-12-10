import sys
import subprocess

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments provided.")
        exit(1)
    if len(sys.argv) > 2:
        print("Too many arguments provided")
        exit(1)

    device_name = sys.argv[1]

    compilation_command = ["gcc", "-o", "display_device_info", "display_device_info.c", "-lpcap"]

    subprocess.run(compilation_command, text=True)

    packet_capture_command = ["sudo", "./display_device_info", device_name]

    process = subprocess.Popen(
        packet_capture_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True 
    )

    line = process.stdout.readline()

    while line:
        print(line.strip())
        line = process.stdout.readline()

    exit_code = process.wait()

    print("Exit code: " + str(exit_code))
    if(exit_code == 0):
        print("Process terminated succesfully")
    else:
        print("Error encountered. Process is still running")
        print("Process is being forcibly terminated")
        process.terminate()