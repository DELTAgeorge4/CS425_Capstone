#!/bin/bash

sudo /usr/bin/python3 snmp_collector.py
sudo /usr/bin/python3 Suricata_to_DB.py
sudo /usr/bin/python3 py_honeypot.py
