import os, time, hashlib, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import vt
from api_client import submit_scan, submit_detection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

class Handler(FileSystemEventHandler):
    def __init__(self, api_key, device_id, token):
        self.api_key = api_key
        self.device_id = device_id
        self.token     = token
        self.scanned   = set()

    def on_created(self, event):
        if event.is_directory: return
        path = event.src_path
        if path in self.scanned: return
        self.scanned.add(path)
        time.sleep(2)
        size = os.path.getsize(path)
        file_hash = get_file_hash(path)
        # Submit scan
        with vt.Client(self.api_key) as client:
            if size <= 32*1024*1024:
                try:
                    report = client.get_object(f"/files/{file_hash}")
                    stats = report.last_analysis_stats
                    status = "completed"
                except vt.error.APIError:
                    upload = client.scan_file(open(path,"rb"), wait_for_completion=False)
                    stats = {}
                    status = "queued"
                payload = {
                    "device_id": self.device_id,
                    "file_path": path,
                    "file_name": os.path.basename(path),
                    "file_size": size,
                    "file_hash": file_hash,
                    "status": status,
                    "is_malicious": stats.get("malicious",0)>0,
                    "malicious_count": stats.get("malicious",0),
                    "suspicious_count": stats.get("suspicious",0),
                    "undetected_count": stats.get("undetected",0),
                    "analysis_id": upload.id if status=="queued" else None,
                    "action_taken": None
                }
                resp = submit_scan(self.token, payload)
                logging.info(f"Scan logged: {resp}")
            else:
                logging.warning("File too large, skipping.")

