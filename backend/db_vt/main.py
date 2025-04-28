from backend.db.main import connect, close, psycopg2

def get_vt_results():
    conn, cur = connect()
    try:
        # Fetch the VT results for the given username
        cur.execute("""
                    SELECT 
    sr.scan_id,
    d.hostname as device_name,
    d.ip_address,
    d.mac_address,
    d.os_type,
    d.os_version,
    sr.file_name,
    sr.file_path,
    sr.file_size,
    sr.scan_time,
    sr.status,
    sr.is_malicious,
    sr.malicious_count,
    sr.suspicious_count,
    sr.undetected_count,
    sr.action_taken
FROM 
    scan_results sr
JOIN 
    devices d ON sr.device_id = d.device_id
ORDER BY 
    sr.scan_time DESC
LIMIT 50;
""")
        # result = cur.fetchall()
                # Get column names from the cursor description
        columns = [desc[0] for desc in cur.description]
        
        # Fetch all results
        results = cur.fetchall()
        
        return results, columns
        
        # return result
    except psycopg2.Error as e:
        print(f"Error fetching VT results: {e}")
        return None
    finally:
        close(conn, cur)
        
if __name__ == "__main__":
    results = get_vt_results()
    if results:
        for row in results:
            print(row)
    else:
        print("No results found.")
        
        