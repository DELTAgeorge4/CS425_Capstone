from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt

from app import models, schemas, database, config

router = APIRouter(prefix="/devices", tags=["devices"])

def create_jwt(device_id: int):
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"device_id": device_id, "exp": expire}
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")

@router.post("/register", response_model=schemas.DeviceRegisterResponse)
def register_device(
    device_in: schemas.DeviceRegister,
    db: Session = Depends(database.get_db)
):
    # Upsert device
    device = (db.query(models.Device)
                .filter_by(hostname=device_in.hostname, mac_address=device_in.mac_address)
                .first())
    if device:
        device.ip_address = device_in.ip_address
        device.os_type    = device_in.os_type
        device.os_version = device_in.os_version
        device.last_seen  = datetime.utcnow()
    else:
        device = models.Device(**device_in.dict())
        db.add(device)
    db.commit()
    db.refresh(device)

    token = create_jwt(device.id)
    return {"device_id": device.id, "token": token}
