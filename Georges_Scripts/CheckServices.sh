#!/bin/bash

# Check systemd services
sudo systemctl status snmp_collector.service
sudo systemctl status Suricata_to_DB.service
sudo systemctl status py_honeypot.service

# Check systemd timers
sudo systemctl status snmp_collector.timer
sudo systemctl status Suricata_to_DB.timer
