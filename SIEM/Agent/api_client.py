import os, requests
from dotenv import load_dotenv

load_dotenv()
SERVER = os.getenv("SERVER_URL")

def register_device(info):
    r = requests.post(f"{SERVER}/devices/register", json=info)
    r.raise_for_status()
    return r.json()  # { device_id, token }

def get_vt_key(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{SERVER}/config/vt_api_key", headers=headers)
    r.raise_for_status()
    return r.json()["vt_api_key"]

def submit_scan(token, payload):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{SERVER}/scans", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def submit_detection(token, payload):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{SERVER}/detections", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()
