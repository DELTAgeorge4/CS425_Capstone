import os
import subprocess
import json
import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

# Load configuration from JSON
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON.")
        sys.exit(1)

# Global config
config = load_config()

def run_snmp_command(command, timeout=2):
    """Run an SNMP command and return the output with timeout"""
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, timeout=timeout)
        return process.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

def host_pingable(host, timeout=0.5):
    """Check if a host is pingable with reduced timeout"""
    command = f"ping -c 1 -W {timeout} {host} > /dev/null 2>&1"
    return os.system(command) == 0

def get_system_info(host, community="public", version=1):
    """Get minimal system information via SNMP using numeric OIDs"""
    # System name (1.3.6.1.2.1.1.5.0 = sysName.0)
    command = f"snmpget -v{version+1}c -c {community} -OQUs udp:{host}:161 1.3.6.1.2.1.1.5.0"
    output = run_snmp_command(command)
    
    if not output:
        return {"ip": host, "hostname": host, "description": "Unknown device"}
    
    hostname = output.split(" = ")[-1].strip('"')
    
    # System description (1.3.6.1.2.1.1.1.0 = sysDescr.0)
    command = f"snmpget -v{version+1}c -c {community} -OQUs udp:{host}:161 1.3.6.1.2.1.1.1.0"
    output = run_snmp_command(command)
    description = output.split(" = ")[-1].strip('"') if output else "Unknown"
    
    print(f"Found device: {hostname} - {description}")
    
    return {
        "ip": host,
        "hostname": hostname,
        "description": description
    }

def get_interfaces(host, community="public", version=1):
    """Get basic interface information via SNMP using numeric OIDs"""
    interfaces = {}
    
    # Get interface descriptions (1.3.6.1.2.1.2.2.1.2 = ifDescr)
    command = f"snmpwalk -v{version+1}c -c {community} -OQUs udp:{host}:161 1.3.6.1.2.1.2.2.1.2"
    output = run_snmp_command(command)
    
    if not output:
        return {}
    
    lines = output.split("\n")
    for line in lines:
        parts = line.split(" = ")
        if len(parts) == 2:
            if_index = parts[0].split(".")[-1]
            if_name = parts[1].strip('"')
            interfaces[if_index] = {"name": if_name}
    
    return interfaces

def get_arp_table(host, community="public", version=1):
    """Get ARP table via SNMP using numeric OIDs"""
    entries = []
    
    # ARP table (1.3.6.1.2.1.4.22.1.2 = ipNetToMediaPhysAddress)
    command = f"snmpwalk -v{version+1}c -c {community} -OQUs udp:{host}:161 1.3.6.1.2.1.4.22.1.2"
    output = run_snmp_command(command)
    
    if not output:
        return []
    
    lines = output.split("\n")
    for line in lines:
        parts = line.split(" = ")
        if len(parts) == 2:
            # Format: 1.3.6.1.2.1.4.22.1.2.if_index.ip1.ip2.ip3.ip4
            oid_parts = parts[0].split(".")
            if len(oid_parts) >= 11:
                if_index = oid_parts[-5]
                ip_addr = ".".join(oid_parts[-4:])
                mac_raw = parts[1].strip('"')
                
                # Format MAC address
                try:
                    mac = mac_raw
                    if ":" in mac_raw:
                        mac = mac_raw
                    else:
                        # If it's in hex-string format with spaces
                        mac_bytes = mac_raw.replace(" ", "")
                        mac = ":".join(mac_bytes[i:i+2] for i in range(0, len(mac_bytes), 2))
                except:
                    mac = mac_raw
                
                entries.append({
                    "if_index": if_index,
                    "ip_addr": ip_addr,
                    "mac_addr": mac
                })
                print(f"ARP entry: {ip_addr} - {mac}")
    
    return entries

def categorize_devices(arp_entries, interfaces):
    """Categorize devices from ARP table based on MAC OUIs and other heuristics"""
    categories = {
        "routers": [],
        "switches": [],
        "servers": [],
        "endpoints": []
    }
    
    # Common networking equipment MAC prefixes
    network_ouis = {
        "9C:05:D6": "Ubiquiti",
        "DC:9F:DB": "Ubiquiti",
        "00:00:0C": "Cisco",
        "00:1A:A1": "Cisco",
        "BC:24:11": "HP Enterprise"
        # Add more as needed
    }
    
    # Common server MAC prefixes
    server_ouis = {
        "00:50:56": "VMware",
        "00:0C:29": "VMware",
        "00:16:3E": "Xen",
        "00:1E:67": "Intel Server",
        "A0:36:9F": "Intel Server"
        # Add more as needed
    }
    
    # Group by interface
    per_interface = {}
    for entry in arp_entries:
        if_index = entry["if_index"]
        if if_index not in per_interface:
            per_interface[if_index] = []
        per_interface[if_index].append(entry)
    
    # Process entries by interface
    for if_index, entries in per_interface.items():
        interface_name = interfaces.get(if_index, {}).get("name", f"Interface {if_index}")
        
        # Group entries by device type
        for entry in entries:
            ip = entry["ip_addr"]
            mac = entry["mac_addr"].upper()
            mac_prefix = mac[:8]
            
            # Skip certain special IPs
            if ip.startswith("169.254.") or ip.startswith("224."):
                continue
                
            # Try to identify device type
            if mac_prefix in network_ouis:
                # This is likely a network device
                if '.1.' in ip or '.254.' in ip:
                    # Likely a router
                    categories["routers"].append({
                        "ip": ip, 
                        "mac": mac, 
                        "vendor": network_ouis[mac_prefix],
                        "interface": interface_name
                    })
                else:
                    # Likely a switch
                    categories["switches"].append({
                        "ip": ip, 
                        "mac": mac,
                        "vendor": network_ouis[mac_prefix],
                        "interface": interface_name
                    })
            elif mac_prefix in server_ouis:
                # This is likely a server
                categories["servers"].append({
                    "ip": ip, 
                    "mac": mac,
                    "vendor": server_ouis[mac_prefix],
                    "interface": interface_name
                })
            else:
                # Regular endpoint
                categories["endpoints"].append({
                    "ip": ip, 
                    "mac": mac,
                    "interface": interface_name
                })
    
    return categories

def create_arp_based_topology(router_ip, community="public", version=1):
    """Create a network topology based solely on ARP tables"""
    # Get router information
    router_info = get_system_info(router_ip, community, version)
    interfaces = get_interfaces(router_ip, community, version)
    
    # Get ARP table
    arp_entries = get_arp_table(router_ip, community, version)
    
    # Categorize devices
    categories = categorize_devices(arp_entries, interfaces)
    
    # Create graph
    G = nx.Graph()
    
    # Add router as central node
    G.add_node(router_ip, **router_info, node_type="router")
    
    # Add discovered devices as nodes and connect to router
    for category, devices in categories.items():
        for device in devices:
            ip = device["ip"]
            if ip != router_ip:  # Don't add router twice
                # Check if device is pingable (alive)
                if host_pingable(ip):
                    # Add basic node data
                    node_data = {
                        "ip": ip,
                        "hostname": device.get("vendor", "") + " " + ip if "vendor" in device else ip,
                        "description": f"{category.rstrip('s')} device with MAC {device['mac']}",
                        "mac_address": device["mac"],
                        "node_type": category.rstrip('s')
                    }
                    
                    # Try to get hostname if it's a server or network device
                    if category in ["routers", "switches", "servers"]:
                        device_info = get_system_info(ip, community, version)
                        if device_info and device_info["hostname"] != ip:
                            node_data.update(device_info)
                    
                    # Add node and edge
                    G.add_node(ip, **node_data)
                    G.add_edge(router_ip, ip, 
                              local_if=device["interface"],
                              protocol="ARP Table")
    
    return G, categories

def visualize_arp_topology(G, output_file="network_topology.png"):
    """Visualize the ARP-based topology using Matplotlib"""
    import math
    
    plt.figure(figsize=(16, 12))
    
    # Create position layout - arrange by device type
    node_positions = {}
    
    # Get nodes by type
    router_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'router']
    switch_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'switch']
    server_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'server']
    endpoint_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'endpoint']
    
    # Custom layout with router in center
    if router_nodes:
        router = router_nodes[0]
        node_positions[router] = (0, 0)  # Center
        
        # Position switches in a circle around the router
        num_switches = len(switch_nodes)
        for i, switch in enumerate(switch_nodes):
            angle = 2 * math.pi * i / max(num_switches, 1)
            node_positions[switch] = (5 * math.cos(angle), 5 * math.sin(angle))
        
        # Position servers in a larger circle
        num_servers = len(server_nodes)
        for i, server in enumerate(server_nodes):
            angle = 2 * math.pi * i / max(num_servers, 1)
            node_positions[server] = (4 * math.cos(angle), 4 * math.sin(angle))
        
        # Position endpoints in the outermost circle
        num_endpoints = len(endpoint_nodes)
        for i, endpoint in enumerate(endpoint_nodes):
            angle = 2 * math.pi * i / max(num_endpoints, 1)
            node_positions[endpoint] = (7 * math.cos(angle), 7 * math.sin(angle))
    else:
        # Fallback to spring layout if no router found
        node_positions = nx.spring_layout(G, k=0.45, iterations=20)
    
    # --- Fallback: assign positions to any nodes not already placed ---
    missing_nodes = set(G.nodes()) - set(node_positions.keys())
    if missing_nodes:
        fallback_positions = nx.spring_layout(G.subgraph(missing_nodes), k=0.45, iterations=20)
        node_positions.update(fallback_positions)
    
    # Draw nodes with different colors by type
    nx.draw_networkx_nodes(G, node_positions, nodelist=router_nodes, node_size=800, 
                             node_color="red", alpha=0.8, label="Router")
    nx.draw_networkx_nodes(G, node_positions, nodelist=switch_nodes, node_size=600, 
                             node_color="green", alpha=0.8, label="Switches")
    nx.draw_networkx_nodes(G, node_positions, nodelist=server_nodes, node_size=500, 
                             node_color="blue", alpha=0.8, label="Servers")
    nx.draw_networkx_nodes(G, node_positions, nodelist=endpoint_nodes, node_size=300, 
                             node_color="gray", alpha=0.8, label="Endpoints")
    
    # Draw edges
    for u, v, data in G.edges(data=True):
        interface = data.get('local_if', '')
        edge_style = '-'
        alpha = 0.6
        
        if 'eth' in interface.lower():
            color = 'blue'
        elif 'wlan' in interface.lower() or 'wifi' in interface.lower():
            color = 'green'
            edge_style = '--'
        elif 'vlan' in interface.lower():
            color = 'purple'
        elif 'br' in interface.lower():
            color = 'orange'
        else:
            color = 'gray'
            
        nx.draw_networkx_edges(G, node_positions, edgelist=[(u, v)], 
                               width=1.5, alpha=alpha, edge_color=color, style=edge_style)
    
    # Draw labels (for routers, switches, and servers use hostnames; endpoints use IP)
    labels = {}
    for node in G.nodes():
        node_data = G.nodes[node]
        if node in router_nodes or node in switch_nodes or node in server_nodes:
            labels[node] = node_data.get('hostname', node)
        else:
            labels[node] = node
    nx.draw_networkx_labels(G, node_positions, labels, font_size=8, font_weight='bold')
    
    # Draw edge labels for router connections
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        if u in router_nodes or v in router_nodes:
            edge_labels[(u, v)] = data.get('local_if', '')
    nx.draw_networkx_edge_labels(G, node_positions, edge_labels, font_size=7)
    
    plt.title("Network Topology (Based on ARP Table)")
    plt.axis("off")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Topology graph saved to {output_file}")
    return output_file

def export_arp_topology_json(G, categories, output_file="network_topology.json"):
    """Export the ARP-based topology data to JSON format"""
    data = {
        "nodes": [],
        "links": [],
        "categories": {k: len(v) for k, v in categories.items()}
    }
    
    # Add nodes
    for node in G.nodes():
        node_data = G.nodes[node]
        data["nodes"].append({
            "id": node,
            "ip": node,
            "hostname": node_data.get('hostname', node),
            "description": node_data.get('description', ''),
            "mac_address": node_data.get('mac_address', ''),
            "node_type": node_data.get('node_type', 'unknown')
        })
    
    # Add links
    for u, v, attrs in G.edges(data=True):
        data["links"].append({
            "source": u,
            "target": v,
            "local_interface": attrs.get('local_if', ''),
            "protocol": attrs.get('protocol', 'ARP Table')
        })
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Topology data exported to {output_file}")
    return output_file

def extend_topology_with_pve(G, pve_nodes, community="public", version=1):
    """
    Query each PVE node for its ARP table and add discovered devices
    and edges to the existing topology graph.
    """
    for pve_ip in pve_nodes:
        print(f"\nQuerying PVE node {pve_ip} for additional ARP entries...")
        interfaces = get_interfaces(pve_ip, community, version)
        arp_entries = get_arp_table(pve_ip, community, version)
        categories = categorize_devices(arp_entries, interfaces)
        
        for category, devices in categories.items():
            for device in devices:
                ip = device["ip"]
                # Only add the node if it doesn't already exist
                if ip not in G:
                    node_data = {
                        "ip": ip,
                        "hostname": device.get("vendor", "") + " " + ip if "vendor" in device else ip,
                        "description": f"{category.rstrip('s')} device with MAC {device['mac']}",
                        "mac_address": device["mac"],
                        "node_type": category.rstrip('s')
                    }
                    G.add_node(ip, **node_data)
                # Add an edge between the PVE node and this discovered device
                G.add_edge(pve_ip, ip, local_if=device["interface"], protocol="ARP Table")
    return G

def main():
    # Get topology configuration from JSON config
    topology_config = config.get('TOPOLOGY', {})
    router_ips = topology_config.get('HOSTS', ['192.168.14.1'])
    community = topology_config.get('COMMUNITY', 'public')
    version = topology_config.get('SNMP_VERSION', 1)  # 0 for SNMP v1, 1 for SNMP v2c
    
    # For simplicity, we'll use the first router IP in the list
    router_ip = router_ips[0] if router_ips else '192.168.14.1'
    
    print(f"Creating network topology based on ARP table from {router_ip}")
    
    # Create topology from the router's ARP table
    G, categories = create_arp_based_topology(router_ip, community, version)
    
    # Print initial summary
    print("\nInitial Network Topology Summary:")
    print(f"- Routers: {len(categories['routers'])}")
    print(f"- Switches: {len(categories['switches'])}")
    print(f"- Servers: {len(categories['servers'])}")
    print(f"- Endpoints: {len(categories['endpoints'])}")
    print(f"- Total devices discovered: {sum(len(c) for c in categories.values())}")
    
    # Automatically discover PVE nodes from the ARP scan based on hostnames
    pve_nodes = [n for n, data in G.nodes(data=True) if "pve" in data.get("hostname", "").lower()]
    print(f"Discovered PVE nodes: {pve_nodes}")
    
    # Extend the topology with ARP data from each discovered PVE node
    if pve_nodes:
        G = extend_topology_with_pve(G, pve_nodes, community, version)
    
    # Check if debug mode is enabled
    debug_mode = config.get('DEBUG_MODE', False)
    if debug_mode:
        print("\nDebug information:")
        print(f"- Number of nodes after PVE extension: {len(G.nodes())}")
        print(f"- Number of edges after PVE extension: {len(G.edges())}")
    
    # Visualize and export the extended topology
    topology_image = visualize_arp_topology(G)
    topology_json = export_arp_topology_json(G, categories)
    
    print(f"\nNetwork topology discovery complete. Results saved to {topology_image} and {topology_json}.")

if __name__ == "__main__":
    main()