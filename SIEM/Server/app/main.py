from fastapi import FastAPI
from app.routers import devices, config, scans, detections
from app.database import engine
from app.models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(devices.router)
app.include_router(config.router)
app.include_router(scans.router)
app.include_router(detections.router)
