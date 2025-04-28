#!/bin/bash

sudo cp -r /opt/total_virus/Services/* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable file_mon.service
sudo systemctl start file_mon.service