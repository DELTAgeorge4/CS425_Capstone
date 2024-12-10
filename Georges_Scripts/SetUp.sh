#!/bin/bash

# Add Directory to bin
echo 'export PATH="/home/CS425_Capstone/Georges_Scripts:$PATH"' | sudo tee -a ~/.bashrc > /dev/null
source ~/.bashrc
./SetTime.sh

# Update and install dependancys
sudo apt update
sudo apt install fping python3-scapy snmp snmpd libsnmp-dev python3-pysnmp4 postgresql suricata python3-psycopg2 python3-watchdog -y
sudo apt full-upgrade -y

# Run python script to set up databases
sudo /usr/bin/python3 /home/CS425_Capstone/Georges_Scripts/Make_Tables.py

# Move files where they need to go
sudo rm /etc/snmp/snmpd.conf
sudo cp Confs/snmpd.conf /etc/snmp/
sudo cp -r Services/* /etc/systemd/system/

# Reload new systemd services into system
sudo systemctl daemon-reload

# Enable Services
sudo systemctl enable snmp_collector.timer
sudo systemctl enable Suricata_to_DB.timer
sudo systemctl enable py_honeypot.service
sudo systemctl enable SMTP.service

# Start Services
sudo systemctl start snmp_collector.timer
sudo systemctl start Suricata_to_DB.timer
sudo systemctl start py_honeypot.service
sudo systemctl start SMTP.service
