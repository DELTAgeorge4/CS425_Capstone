import os, socket, platform, uuid
from dotenv import load_dotenv
from api_client import register_device, get_vt_key
from scanner import Handler
from watchdog.observers import Observer

load_dotenv()

# 1) Device info
hostname = socket.gethostname()
ip       = socket.gethostbyname(hostname)
mac      = ':'.join(f"{(uuid.getnode()>>i)&0xff:02x}" 
                   for i in range(0,48,8)[::-1])
os_type  = platform.system()
os_ver   = platform.version()

info = {
    "hostname": hostname,
    "ip_address": ip,
    "mac_address": mac,
    "os_type": os_type,
    "os_version": os_ver
}

# 2) Register & fetch token + VT key
reg = register_device(info)
device_id, token = reg["device_id"], reg["token"]
vt_key = get_vt_key(token)

# 3) Start watcher
from scanner import Handler
downloads = os.path.expanduser("~/Downloads")
handler = Handler(vt_key, device_id, token)
obs = Observer()
obs.schedule(handler, downloads, recursive=False)
obs.start()
print(f"Watching {downloads}. Ctrl+C to stop.")
try:
    obs.join()
except KeyboardInterrupt:
    obs.stop()
    obs.join()
