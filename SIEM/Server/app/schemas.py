from pydantic import BaseModel
from typing import Optional, Dict

# --- Devices ---
class DeviceRegister(BaseModel):
    hostname: str
    ip_address: Optional[str]
    mac_address: Optional[str]
    os_type: Optional[str]
    os_version: Optional[str]

class DeviceRegisterResponse(BaseModel):
    device_id: int
    token: str

# --- Scans ---
class ScanCreate(BaseModel):
    device_id: int
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    status: str
    is_malicious: Optional[bool]
    malicious_count: Optional[int]
    suspicious_count: Optional[int]
    undetected_count: Optional[int]
    analysis_id: Optional[str]
    action_taken: Optional[str]

class ScanResponse(BaseModel):
    scan_id: int

# --- Detections ---
class DetectionCreate(BaseModel):
    scan_id: int
    device_id: int
    file_hash: str
    quarantined: bool
    quarantine_path: Optional[str]
    notes: Optional[str]

class DetectionResponse(BaseModel):
    detection_id: int

# --- PendingAnalyses ---
class PendingAnalysisCreate(BaseModel):
    file_path: str
    file_hash: str
    analysis_id: str

# --- Config ---
class VTKeyResponse(BaseModel):
    vt_api_key: str
