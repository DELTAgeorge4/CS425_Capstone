
#to run /home/CS425_Capstone$ python3 -m backend.total_virus.main 
import sys
# import subprocess
import os

# Add parent directory to path if running directly
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.append(parent_dir)

# Now imports
import time
import vt
import hashlib
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socket
import platform
import uuid
import psycopg2
import config  # Import your config module



def connect():
    try:
        conn = psycopg2.connect(
            dbname= config.DB_NAME,  # Ensure this matches your database name
            user= config.DB_USER,  # Use the user from your config
            password= config.DB_PASSWORD,  # Use the password you set
            host=config.DB_HOST,  # Use the host from your config
        )
        cur = conn.cursor()
        return conn, cur
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise SystemExit("Database connection failed.")


# Function to close the database connection
def close(conn, cur):
    try:
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error closing the database connection: {e}")
        
        
        
        
# Configure logging with both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('virus_scan.log'),
        logging.StreamHandler()  # This will print to console
    ]
)

user = os.environ.get('USER')
print("The user is : ", user)
PATH_TO_MONITOR = os.path.join("/home", user, "Downloads")
print("The path to monitor is : ", PATH_TO_MONITOR)

# Database functions
def get_device_info():
    # get device information
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    try:
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0, 48, 8)][::-1])
    except:
        mac_address = "unknown"
    
    os_type = platform.system()
    os_version = platform.version()
    
    return {
        'hostname': hostname,
        'ip_address': ip_address,
        'mac_address': mac_address,
        'os_type': os_type,
        'os_version': os_version
    }

def register_or_update_device():
    # put device in database
    device_info = get_device_info()
    
    conn, cur = connect()
    
    try:
        # Insert device if it doesn't exist, otherwise update last_seen
        cur.execute("""
        INSERT INTO devices (hostname, ip_address, mac_address, os_type, os_version)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (hostname, mac_address) 
        DO UPDATE SET 
            ip_address = EXCLUDED.ip_address,
            last_seen = CURRENT_TIMESTAMP
        RETURNING device_id
        """, (device_info['hostname'], device_info['ip_address'], 
              device_info['mac_address'], device_info['os_type'], 
              device_info['os_version']))
        
        device_id = cur.fetchone()[0]
        conn.commit()
        return device_id
    except psycopg2.Error as e:
        logging.error(f"Error registering device: {e}")
        conn.rollback()
        return None
    finally:
        close(conn, cur)

def log_scan_result(device_id, file_path, file_hash, file_size, status, 
                   is_malicious=None, stats=None, analysis_id=None, action_taken=None):
    """Log scan result to database"""
    conn, cur = connect()
    
    try:
        file_name = os.path.basename(file_path)
        malicious_count = stats.get('malicious', 0) if stats else 0
        suspicious_count = stats.get('suspicious', 0) if stats else 0
        undetected_count = stats.get('undetected', 0) if stats else 0
        
        cur.execute("""
        INSERT INTO scan_results 
        (device_id, file_path, file_name, file_size, file_hash, status, 
         is_malicious, malicious_count, suspicious_count, undetected_count, 
         analysis_id, action_taken)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING scan_id
        """, (device_id, file_path, file_name, file_size, file_hash, status,
              is_malicious, malicious_count, suspicious_count, undetected_count,
              analysis_id, action_taken))
        
        scan_id = cur.fetchone()[0]
        conn.commit()
        return scan_id
    except psycopg2.Error as e:
        logging.error(f"Error logging scan result: {e}")
        conn.rollback()
        return None
    finally:
        close(conn, cur)

def log_malware_detection(scan_id, device_id, file_hash, quarantined=False, 
                         quarantine_path=None, notes=None):
    """Log malware detection to database"""
    conn, cur = connect()
    
    try:
        cur.execute("""
        INSERT INTO malware_detections
        (scan_id, device_id, file_hash, quarantined, quarantine_path, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING detection_id
        """, (scan_id, device_id, file_hash, quarantined, quarantine_path, notes))
        
        detection_id = cur.fetchone()[0]
        conn.commit()
        return detection_id
    except psycopg2.Error as e:
        logging.error(f"Error logging malware detection: {e}")
        conn.rollback()
        return None
    finally:
        close(conn, cur)

def log_pending_analysis(file_path, file_hash, analysis_id):
    """Log pending analysis to database"""
    conn, cur = connect()
    
    try:
        cur.execute("""
        INSERT INTO pending_analyses
        (file_path, file_hash, analysis_id)
        VALUES (%s, %s, %s)
        """, (file_path, file_hash, analysis_id))
        
        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Error logging pending analysis: {e}")
        conn.rollback()
    finally:
        close(conn, cur)

# Function to calculate SHA-256 hash of a file
def get_file_hash(file_path):
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return None

# VirusTotal scan function with database logging
def scan_file(file_path, api_key, device_id):
    try:
        # Skip files that are too large (VirusTotal has a 32MB limit for free accounts)
        file_size = os.path.getsize(file_path)
        if file_size > 32 * 1024 * 1024:  # 32MB in bytes
            logging.warning(f"File too large to scan: {file_path} ({file_size} bytes)")
            log_scan_result(device_id, file_path, "N/A", file_size, "skipped", 
                          is_malicious=False, action_taken="skipped - too large")
            return False, "File too large for scanning"
            
        # Calculate file hash
        file_hash = get_file_hash(file_path)
        if not file_hash:
            return False, "Could not calculate file hash"
            
        logging.info(f"Scanning file: {file_path}")
        logging.info(f"File size: {file_size} bytes")
        logging.info(f"File hash: {file_hash}")
        
        # Create the client
        with vt.Client(api_key) as client:
            # First try to get existing file analysis by hash
            try:
                file_report = client.get_object(f"/files/{file_hash}")
                logging.info(f"File already analyzed previously")
                
                # Get scan results
                stats = file_report.last_analysis_stats
                logging.info(f"Detection stats: {stats}")
                
                is_malicious = stats.get('malicious', 0) > 0 or stats.get('suspicious', 0) > 0
                
                # Log the scan result
                scan_id = log_scan_result(
                    device_id=device_id,
                    file_path=file_path,
                    file_hash=file_hash,
                    file_size=file_size,
                    status="completed",
                    is_malicious=is_malicious,
                    stats=stats,
                    action_taken="none" if not is_malicious else "quarantined"
                )
                
                if is_malicious:
                    logging.warning(f"ALERT: Potentially malicious file detected: {file_path}")
                    logging.warning(f"Malicious: {stats.get('malicious', 0)}, Suspicious: {stats.get('suspicious', 0)}")
                    return False, f"Potentially malicious file: {stats.get('malicious', 0)} detections", scan_id
                else:
                    logging.info(f"File appears safe: {file_path}")
                    return True, "File is safe", scan_id
                    
            except vt.error.APIError as e:
                logging.info(f"File not previously analyzed: {e}")
                
                # Upload file for scanning
                try:
                    logging.info("Uploading file for scanning...")
                    with open(file_path, "rb") as f:
                        upload_result = client.scan_file(f, wait_for_completion=False)
                        analysis_id = upload_result.id
                    logging.info(f"Analysis ID: {analysis_id}")
                    
                    # Log the pending analysis
                    log_pending_analysis(file_path, file_hash, analysis_id)
                    
                    # Log initial scan submission
                    scan_id = log_scan_result(
                        device_id=device_id,
                        file_path=file_path,
                        file_hash=file_hash,
                        file_size=file_size,
                        status="queued",
                        analysis_id=analysis_id
                    )
                    
                    # Manual polling
                    max_attempts = 12
                    status = "queued"
                    for attempt in range(max_attempts):
                        logging.info(f"Attempt {attempt+1}/{max_attempts} to check analysis status...")
                        time.sleep(10)  # Wait 10 seconds between checks
                        
                        try:
                            # Try to get analysis status
                            analysis = client.get_object(f"/analyses/{analysis_id}")
                            status = analysis.status
                            logging.info(f"Current status: {status}")
                            
                            if status == "completed":
                                stats = analysis.stats
                                logging.info(f"Scan completed! Malicious: {stats.get('malicious', 0)}, Suspicious: {stats.get('suspicious', 0)}")
                                
                                is_malicious = stats.get('malicious', 0) > 0 or stats.get('suspicious', 0) > 0
                                
                                # Update the scan result status
                                conn, cur = connect()
                                cur.execute("""
                                UPDATE scan_results 
                                SET status = %s, is_malicious = %s, malicious_count = %s, 
                                    suspicious_count = %s, undetected_count = %s
                                WHERE scan_id = %s
                                """, ("completed", is_malicious, stats.get('malicious', 0),
                                      stats.get('suspicious', 0), stats.get('undetected', 0), scan_id))
                                conn.commit()
                                close(conn, cur)
                                
                                if is_malicious:
                                    logging.warning(f"ALERT: Potentially malicious file detected: {file_path}")
                                    return False, f"Potentially malicious file: {stats.get('malicious', 0)} detections", scan_id
                                else:
                                    logging.info(f"File appears safe: {file_path}")
                                    return True, "File is safe", scan_id
                        except vt.error.APIError as poll_error:
                            logging.error(f"Error checking status: {poll_error}")
                    
                    if status != "completed":
                        logging.warning(f"Analysis not completed within timeout period for {file_path}")
                        return None, "Analysis timeout", scan_id
                        
                except vt.error.APIError as upload_error:
                    logging.error(f"Error uploading file: {upload_error}")
                    return None, f"Upload error: {upload_error}", None
                    
    except Exception as e:
        logging.error(f"Unexpected error scanning {file_path}: {e}")
        return None, f"Unexpected error: {e}", None

# File system event handler
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, api_key, device_id):
        self.api_key = api_key
        self.device_id = device_id
        self.processed_files = set()
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # Skip log files and Python files to avoid issues
        if file_path.endswith('.log') or file_path.endswith('.py') or file_path.endswith('.pyc'):
            return
            
        # Avoid duplicate processing
        if file_path in self.processed_files:
            return
            
        self.processed_files.add(file_path)
        logging.info(f"New file detected: {file_path}")
        
        # Wait a moment to ensure file is fully written
        time.sleep(2)
        
        # Check if file still exists (might have been moved/deleted)
        if not os.path.exists(file_path):
            logging.info(f"File no longer exists: {file_path}")
            return
            
        # Scan the file
        result = scan_file(file_path, self.api_key, self.device_id)
        is_safe = result[0]
        message = result[1]
        scan_id = result[2] if len(result) > 2 else None
        
        if is_safe is False:
            logging.warning(f"Action required for {file_path}: {message}")
            print(f"\n⚠️ WARNING: Potentially malicious file detected: {file_path}")
            print(f"Message: {message}")
            
            # Move to quarantine
            quarantine_dir = os.path.expanduser("~/quarantine")
            os.makedirs(quarantine_dir, exist_ok=True)
            quarantine_path = os.path.join(quarantine_dir, os.path.basename(file_path))
            try:
                os.rename(file_path, quarantine_path)
                logging.info(f"Moved suspicious file to quarantine: {quarantine_path}")
                print(f"File moved to quarantine: {quarantine_path}")
                
                # Log the malware detection
                file_hash = get_file_hash(quarantine_path)
                if scan_id:
                    log_malware_detection(
                        scan_id=scan_id,
                        device_id=self.device_id,
                        file_hash=file_hash,
                        quarantined=True,
                        quarantine_path=quarantine_path,
                        notes=message
                    )
            except OSError as e:
                logging.error(f"Could not move file to quarantine: {e}")
        else:
            print(f"✅ File scanned and appears safe: {file_path}")

# Main function
def main():
    # Configuration
    # api_key_path = config.VIRUSTOTAL_API_KEY_PATH  # Path to your API key file
    downloads_dir = PATH_TO_MONITOR  # Your download directory
    
    # Read API key
    # with open(api_key_path, "r") as f:
    #     api_key = f.read().strip()
    
    api_key = config.VIRUSTOTAL_API_KEY  # Replace with your actual API key
    # Register or update device
    device_id = register_or_update_device()
    if not device_id:
        logging.error("Failed to register device. Exiting.")
        return
    
    print(f"Starting file monitor for directory: {downloads_dir}")
    print(f"Device registered with ID: {device_id}")
    print(f"Waiting for new files to be downloaded...")
    print("Press Ctrl+C to stop monitoring")
    logging.info(f"Starting file monitor for directory: {downloads_dir}")
    
    # Create and start the file system observer
    event_handler = NewFileHandler(api_key, device_id)
    observer = Observer()
    observer.schedule(event_handler, downloads_dir, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nFile monitoring stopped.")
    observer.join()

if __name__ == "__main__":
    main()