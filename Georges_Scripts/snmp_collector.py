import os
import subprocess
from subprocess import PIPE

# gets uptime, cpu usage, ram usage, and disk usage, hostname

current_dir = os.path.dirname(os.path.realpath(__file__))

def host_pingable(host):
    command = f"/usr/bin/fping -q -c 2 -p 500 -t 500 -O 0 {host}"
    if os.system(command) == 0:
        return True
    return False

def process_host_data(host):
    command = f"/usr/bin/snmpget -v2c -c public -OQXUte -Pu udp:{host}:161 -M {current_dir}/mibs SNMPv2-MIB::sysName.0"
    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Error: {stderr}")
        return None
    output = stdout.decode().split("\n")
    return {
        "hostname": output[0].split(" = ")[-1]
    }

def process_uptime_data(host):
    command = f"/usr/bin/snmpget -v2c -c public -OQXUte -Pu udp:{host}:161 -M {current_dir}/mibs HOST-RESOURCES-MIB::hrSystemUptime.0"
    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Error: {stderr}")
        return None
    output = stdout.decode().split("\n")
    return {
        "system_uptime": int(output[0].split(" = ")[-1]) / 8640000 # convert to days
    }

def process_cpu_usage_data(host):
    command = f"/usr/bin/snmpget -v2c -c public -OQXUte -Pu udp:{host}:161 -M {current_dir}/mibs UCD-SNMP-MIB::ssCpuUser.0"
    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Error: {stderr}")
        return None
    output = stdout.decode().split("\n")
    return {
        "cpu_usage": float(output[0].split(" = ")[-1])
    }

def process_ram_usage_data(host):
    virtal_mem = -1
    cached_mem = -1
    total_mem = -1
    mem_conversion = 1 / (1024 * 1024)
    command = f"/usr/bin/snmpget -v2c -c public -OUQn -M {current_dir}/mibs udp:{host}:161 .1.3.6.1.2.1.25.2.3.1.6.1 .1.3.6.1.2.1.25.2.3.1.6.7 .1.3.6.1.4.1.2021.4.5.0"
    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Error: {stderr}")
        return None
    output = stdout.decode().split("\n")
    for i in range(len(output)):
        if i == 0:
            virtal_mem = int(output[i].split(" = ")[-1])
        if i == 1:
            cached_mem = int(output[i].split(" = ")[-1])
        if i == 2:
            total_mem = int(output[i].split(" = ")[-1])
    return {
        "ram_used": (virtal_mem - cached_mem) * mem_conversion,
        "ram_total": total_mem * mem_conversion,
        "ram_percent_used": ((virtal_mem - cached_mem) / total_mem) * 100
    }
        

def process_disk_usage_date(host):
    root_dir_used_storage = ""
    root_dir_total_storage = ""
    disk_conversion = 4096 / (1000 * 1000 * 1000)
    command = f"snmpbulkwalk -v2c -c public -OQUs -m HOST-RESOURCES-MIB:HOST-RESOURCES-TYPES -M {current_dir}/mibs udp:{host}:161 hrStorageEntry"
    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Error: {stderr}")
        return None
    for line in stdout.decode().split("\n"):
        if "hrStorageUsed.31" in line:
            root_dir_used_storage = int(line.split(" = ")[-1]) * disk_conversion
        if "hrStorageSize.31" in line:
            root_dir_total_storage = int(line.split(" = ")[-1]) * disk_conversion
    return {
        "root_dir_used_storage": root_dir_used_storage,
        "root_dir_total_storage": root_dir_total_storage,
        "root_dir_percent_used": (root_dir_used_storage / root_dir_total_storage) * 100
    }

# gets cpu, ram, disk usage, and uptime
def get_host_data(host):
    if host_pingable(host):
        print(process_disk_usage_date(host))
        print(process_cpu_usage_data(host))
        print(process_ram_usage_data(host))
        print(process_uptime_data(host))
        print(process_host_data(host))
    else:
        print("Host is not pingable")

if __name__ == "__main__":
    get_host_data("192.168.14.14")
