#!/bin/bash

# Add Directory to bin
echo 'export PATH="/home/CS425_Capstone/Georges_Scripts:$PATH"' | sudo tee -a ~/.bashrc > /dev/null
source ~/.bashrc
./SetTime.sh

# Update and install dependancys
sudo apt update
sudo apt install fping python3-scapy snmp snmpd libsnmp-dev python3-pysnmp4 postgresql suricata python3-psycopg2 -y
sudo apt full-upgrade -y

# Move files where they need to go
sudo rm /etc/snmp/snmpd.conf
sudo cp snmpd.conf /etc/snmp/
