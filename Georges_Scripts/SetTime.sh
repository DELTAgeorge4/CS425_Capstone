#!/bin/bash

# Define an array of US time zones
timezones=(
  "America/New_York"
  "America/Chicago"
  "America/Denver"
  "America/Los_Angeles"
  "America/Phoenix"
  "America/Anchorage"
  "Pacific/Honolulu"
)

# Display the list of time zones
echo "Please choose a time zone from the list below:"
for i in "${!timezones[@]}"; do
  echo "$((i+1))) ${timezones[$i]}"
done

# Prompt user for selection
read -p "Enter the number corresponding to your choice: " choice

# Validate user input
if [[ $choice -ge 1 && $choice -le ${#timezones[@]} ]]; then
  # Get the selected time zone
  selected_timezone=${timezones[$((choice-1))]}
  
  # Set the time zone
  echo "Setting the time zone to $selected_timezone..."
  sudo timedatectl set-timezone "$selected_timezone"
  
  # Confirm the change
  echo "Time zone set successfully to $(timedatectl | grep 'Time zone')"
else
  echo "Invalid choice. Please run the script again and select a valid number."
fi

