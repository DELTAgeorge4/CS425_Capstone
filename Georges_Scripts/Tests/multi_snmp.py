from concurrent.futures import ThreadPoolExecutor

def process_host(host):
    print(f"Processing host: {host}")
    collected_data = get_host_data(host)
    if collected_data:
        insert_into_postgres(collected_data)

if __name__ == "__main__":
    hosts = ["192.168.14.14", "192.168.14.15", "192.168.14.16"]  # Add your list of hosts here
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
        executor.map(process_host, hosts)
