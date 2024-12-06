import subprocess

def read_until_input_needed(process):
    output = []
    while True:
        line = process.stdout.readline()
        if not line:  # Waiting to be prompted for input
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

    process.stdin.write(choice)
    process.stdin.flush()

    
