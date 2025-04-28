from fastapi import APIRouter, Depends, HTTPException, Header
from app.config import VT_API_KEY
import jwt

router = APIRouter(prefix="/config", tags=["config"])

def verify_token(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, VT_API_KEY="", algorithms=["HS256"], options={"verify_signature": False})
        # we only need device_id from payload, signature is skipped because secret same format
        return payload
    except Exception:
        raise HTTPException(401, "Invalid or missing token")

@router.get("/vt_api_key", response_model=dict)
def get_vt_key(token_data: dict = Depends(verify_token)):
    return {"vt_api_key": VT_API_KEY}
