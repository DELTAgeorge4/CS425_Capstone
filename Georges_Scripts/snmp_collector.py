import os
import subprocess
from subprocess import PIPE
import psycopg2
from psycopg2 import sql
from datetime import datetime
import config

# Database connection details
DB_HOST = config.DB_HOST
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD


current_dir = os.path.dirname(os.path.realpath(__file__))

def host_pingable(host):
    command = f"/usr/bin/fping -q -c 2 -p 500 -t 500 -O 0 {host} > /dev/null 2>&1"
    return os.system(command) == 0

def run_snmp_command(command):
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return None

def process_host_data(host):
    command = f"/usr/bin/snmpget -v2c -c public -OQXUte -Pu udp:{host}:161 -M {current_dir}/mibs SNMPv2-MIB::sysName.0"
    output = run_snmp_command(command)
    if output:
        return {"hostname": output.split(" = ")[-1]}
    return {"hostname": None}

def process_uptime_data(host):
    command = f"/usr/bin/snmpget -v2c -c public -OQXUte -Pu udp:{host}:161 -M {current_dir}/mibs HOST-RESOURCES-MIB::hrSystemUptime.0"
    output = run_snmp_command(command)
    if output:
        uptime_ticks = int(output.split(" = ")[-1])
        return {"system_uptime": round(uptime_ticks / 8640000, 2)}  # Convert to days
    return {"system_uptime": None}

def process_cpu_usage_data(host):
    command = f"/usr/bin/snmpget -v2c -c public -OQXUte -Pu udp:{host}:161 -M {current_dir}/mibs UCD-SNMP-MIB::ssCpuUser.0"
    output = run_snmp_command(command)
    if output:
        return {"cpu_usage": round(float(output.split(" = ")[-1]), 2)}
    return {"cpu_usage": None}

def process_ram_usage_data(host):
    command = f"/usr/bin/snmpget -v2c -c public -OUQn -M {current_dir}/mibs udp:{host}:161 .1.3.6.1.2.1.25.2.3.1.6.1 .1.3.6.1.2.1.25.2.3.1.6.7 .1.3.6.1.4.1.2021.4.5.0"
    output = run_snmp_command(command)
    if output:
        values = [int(line.split(" = ")[-1]) for line in output.split("\n")]
        ram_used = round((values[0] - values[1]) / (1024 * 1024), 2)
        ram_total = round(values[2] / (1024 * 1024), 2)
        ram_percent_used = round((ram_used / ram_total) * 100, 2)
        return {
            "ram_used": ram_used,
            "ram_total": ram_total,
            "ram_percent_used": ram_percent_used
        }
    return {"ram_used": None, "ram_total": None, "ram_percent_used": None}

def process_disk_usage_data(host):
    command = f"snmpbulkwalk -v2c -c public -OQUs -m HOST-RESOURCES-MIB:HOST-RESOURCES-TYPES -M {current_dir}/mibs udp:{host}:161 hrStorageEntry"
    output = run_snmp_command(command)
    if output:
        lines = output.split("\n")
        root_dir_used = root_dir_total = file_desc = -1
        for line in lines:
            if line.endswith(" = /"):
                file_desc = line.split(" = ")[0].split(".")[-1]
            elif file_desc != -1:
                if f"hrStorageUsed.{file_desc}" in line:
                    root_dir_used = round(int(line.split(" = ")[-1]) * 4096 / (1000 ** 3), 2)
                elif f"hrStorageSize.{file_desc}" in line:
                    root_dir_total = round(int(line.split(" = ")[-1]) * 4096 / (1000 ** 3), 2)
        if root_dir_used != -1 and root_dir_total != -1:
            return {
                "root_dir_used_storage": root_dir_used,
                "root_dir_total_storage": root_dir_total,
                "root_dir_percent_used": round((root_dir_used / root_dir_total) * 100, 2)
            }
    return {"root_dir_used_storage": None, "root_dir_total_storage": None, "root_dir_percent_used": None}

def get_host_data(host):
    if host_pingable(host):
        data = {}
        data.update(process_host_data(host))
        data.update(process_uptime_data(host))
        data.update(process_cpu_usage_data(host))
        data.update(process_ram_usage_data(host))
        data.update(process_disk_usage_data(host))
        return data
    else:
        print("Host is not pingable.")
        return None

def insert_into_postgres(data):
    try:
        with psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    INSERT INTO snmp_metrics (
                        hostname, system_uptime, cpu_usage, ram_used, ram_total, ram_percent_used,
                        root_dir_used_storage, root_dir_total_storage, root_dir_percent_used, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """)
                cur.execute(query, (
                    data["hostname"], data["system_uptime"], data["cpu_usage"],
                    data["ram_used"], data["ram_total"], data["ram_percent_used"],
                    data["root_dir_used_storage"], data["root_dir_total_storage"],
                    data["root_dir_percent_used"], datetime.now()
                ))
                #print("Data inserted successfully.")
    except psycopg2.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    host = "192.168.14.14"
    collected_data = get_host_data(host)
    if collected_data:
        #print(collected_data)
        insert_into_postgres(collected_data)
