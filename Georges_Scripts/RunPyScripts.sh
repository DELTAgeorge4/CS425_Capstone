#!/bin/bash

/usr/bin/python3 snmp_collector.py
/usr/bin/python3 py_honeypot.py
/usr/bin/python3 Suricata_to_DB.py
