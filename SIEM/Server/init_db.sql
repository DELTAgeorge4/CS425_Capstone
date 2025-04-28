CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- devices table
CREATE TABLE devices (
    id            SERIAL PRIMARY KEY,
    hostname      TEXT NOT NULL,
    ip_address    TEXT,
    mac_address   TEXT,
    os_type       TEXT,
    os_version    TEXT,
    last_seen     TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(hostname, mac_address)
);

-- scan_results table
CREATE TABLE scan_results (
    id               SERIAL PRIMARY KEY,
    device_id        INTEGER NOT NULL REFERENCES devices(id),
    file_path        TEXT NOT NULL,
    file_name        TEXT NOT NULL,
    file_size        BIGINT,
    file_hash        TEXT,
    status           TEXT,
    is_malicious     BOOLEAN,
    malicious_count  INTEGER,
    suspicious_count INTEGER,
    undetected_count INTEGER,
    analysis_id      TEXT,
    action_taken     TEXT,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- malware_detections
CREATE TABLE malware_detections (
    id              SERIAL PRIMARY KEY,
    scan_id         INTEGER NOT NULL REFERENCES scan_results(id),
    device_id       INTEGER NOT NULL REFERENCES devices(id),
    file_hash       TEXT,
    quarantined     BOOLEAN,
    quarantine_path TEXT,
    notes           TEXT,
    detected_at     TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- pending_analyses
CREATE TABLE pending_analyses (
    id           SERIAL PRIMARY KEY,
    file_path    TEXT NOT NULL,
    file_hash    TEXT NOT NULL,
    analysis_id  TEXT NOT NULL,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT now()
);
