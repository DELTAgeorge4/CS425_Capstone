import subprocess
import sys

def is_service_running(service_name):
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", service_name],
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking service status: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments provided.")
        exit(1)
    if len(sys.argv) > 2:
        print("Too many arguments provided")
        exit(1)

    SERVICE = "nss_sniffer_" + sys.argv[1]
    if is_service_running(SERVICE):
        print(f"{SERVICE} is running.")
    else:
        print(f"{SERVICE} is not running.")
