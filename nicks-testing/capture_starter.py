import subprocess

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

if __name__ == "__main__":
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
    print(line.strip())

    line = process.stdout.readline()
    print(line.strip())

    line = process.stdout.readline()
    print(line.strip())

    line = process.stdout.readline()
    print(line.strip())

    exit_code = process.wait()

    print("Exit code: " + str(exit_code))



    
