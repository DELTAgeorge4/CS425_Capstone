from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import jwt

from app import models, schemas, database, config

router = APIRouter(prefix="/scans", tags=["scans"])

def get_current_device(authorization: str = Header(...)):
    scheme, token = authorization.split()
    payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    return payload["device_id"]

@router.post("/", response_model=schemas.ScanResponse)
def submit_scan(
    scan_in: schemas.ScanCreate,
    device_id: int = Depends(get_current_device),
    db: Session = Depends(database.get_db)
):
    if scan_in.device_id != device_id:
        raise HTTPException(403, "Device ID mismatch")
    scan = models.ScanResult(**scan_in.dict())
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return {"scan_id": scan.id}
