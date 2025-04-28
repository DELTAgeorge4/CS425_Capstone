from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import jwt

from app import models, schemas, database, config

router = APIRouter(prefix="/detections", tags=["detections"])

def get_current_device(authorization: str = Header(...)):
    scheme, token = authorization.split()
    payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    return payload["device_id"]

@router.post("/", response_model=schemas.DetectionResponse)
def submit_detection(
    det_in: schemas.DetectionCreate,
    device_id: int = Depends(get_current_device),
    db: Session = Depends(database.get_db)
):
    if det_in.device_id != device_id:
        raise HTTPException(403, "Device ID mismatch")
    det = models.MalwareDetection(**det_in.dict())
    db.add(det)
    db.commit()
    db.refresh(det)
    return {"detection_id": det.id}
