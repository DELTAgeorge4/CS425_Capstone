from sqlalchemy import (
    Column, Integer, String, Boolean, BigInteger, Text, TIMESTAMP, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    id          = Column(Integer, primary_key=True, index=True)
    hostname    = Column(Text, nullable=False)
    ip_address  = Column(Text)
    mac_address = Column(Text)
    os_type     = Column(Text)
    os_version  = Column(Text)
    last_seen   = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class ScanResult(Base):
    __tablename__ = "scan_results"
    id               = Column(Integer, primary_key=True, index=True)
    device_id        = Column(Integer, ForeignKey("devices.id"), nullable=False)
    file_path        = Column(Text, nullable=False)
    file_name        = Column(Text, nullable=False)
    file_size        = Column(BigInteger)
    file_hash        = Column(Text)
    status           = Column(Text)
    is_malicious     = Column(Boolean)
    malicious_count  = Column(Integer)
    suspicious_count = Column(Integer)
    undetected_count = Column(Integer)
    analysis_id      = Column(Text)
    action_taken     = Column(Text)
    created_at       = Column(TIMESTAMP(timezone=True), server_default=func.now())

class MalwareDetection(Base):
    __tablename__ = "malware_detections"
    id              = Column(Integer, primary_key=True, index=True)
    scan_id         = Column(Integer, ForeignKey("scan_results.id"), nullable=False)
    device_id       = Column(Integer, ForeignKey("devices.id"), nullable=False)
    file_hash       = Column(Text)
    quarantined     = Column(Boolean)
    quarantine_path = Column(Text)
    notes           = Column(Text)
    detected_at     = Column(TIMESTAMP(timezone=True), server_default=func.now())

class PendingAnalysis(Base):
    __tablename__ = "pending_analyses"
    id          = Column(Integer, primary_key=True, index=True)
    file_path   = Column(Text, nullable=False)
    file_hash   = Column(Text, nullable=False)
    analysis_id = Column(Text, nullable=False)
    created_at  = Column(TIMESTAMP(timezone=True), server_default=func.now())
