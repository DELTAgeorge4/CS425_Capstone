#!/bin/bash

# Function to display menu
show_menu() {
    echo "What would you like to do?"
    echo "1) Start services"
    echo "2) Stop services"
    echo "3) Exit"
    read -p "Enter your choice (1/2/3): " choice
    echo
}

# Function to start services
start_services() {
    echo "Starting services..."
    sudo systemctl start snmp_collector.timer
    sudo systemctl start Suricata_to_DB.timer
    sudo systemctl start py_honeypot.service
    sudo systemctl start SMTP.service
    echo "All services have been started."
}

# Function to stop services
stop_services() {
    echo "Stopping services..."
    sudo systemctl stop snmp_collector.timer
    sudo systemctl stop Suricata_to_DB.timer
    sudo systemctl stop py_honeypot.service
    sudo systemctl stop SMTP.service
    echo "All services have been stopped."
}

# Main script
while true; do
    show_menu

    case $choice in
        1)
            start_services
            ;;
        2)
            stop_services
            ;;
        3)
            echo "Exiting script."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please enter 1, 2, or 3."
            ;;
    esac
    echo
done
