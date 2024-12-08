#!/bin/bash

sudo systemctl stop snmp_collector.timer
sudo systemctl stop Suricata_to_DB.timer
sudo systemctl stop py_honeypot.service
