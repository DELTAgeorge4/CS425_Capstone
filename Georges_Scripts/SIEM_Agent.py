#!/usr/bin/env python3
from flask import Flask, jsonify
import platform
from datetime import datetime

app = Flask(__name__)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    # For demonstration, return a dummy log entry.
    logs = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "source": platform.system(),  # Returns 'Linux' or 'Windows'
            "event_type": "alert",
            "severity": "high",
            "message": f"Sample log from agent running on {platform.system()}"
        }
    ]
    return jsonify(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
