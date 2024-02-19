#!/bin/bash

exp_id=$1
log_file="$exp_id-output.log"
pid_file="$exp_id-pid.txt"
script_pid_file="$exp_id-script_pid.txt"
size_limit=$((3 * 1024 * 1024))
interval_minute=5

echo "Starting the WattsupPro logger with PID: $$"

# Function to check and manage log file size
check_log_size() {
  size=$(stat -c %s "$log_file")

  if [ "$size" -ge "$size_limit" ]; then
    index=0
    while [ -f "${log_file%.*}_${index}.log" ]; do
      ((index++))
    done
    mv "$log_file" "${log_file%.*}_${index}.log"
    truncate -s "$size_limit" "${log_file%.*}_${index}.log"
  fi
}

# Check if the script is already running
if [ -f "$pid_file" ]; then
  pid=$(cat "$pid_file")
  if ps -p "$pid" >/dev/null; then
    echo "Script is already running with PID: $pid"
    exit 1
  else
    rm "$pid_file" # Remove stale PID file
  fi
fi

# Execute the command in the background and store the PID
(
sudo python3 wattsuppro_logger/WattsupPro.py -l -p /dev/ttyUSB0 2>&1 | tee -a "$log_file"
) &
echo $! >"$pid_file"

echo Launching the WattsupPro logger with PID: "$pid_file"

## Enter a loop to check log file size periodically
#(
#  while true; do
#    sleep $((interval_minute * 60))
#    check_log_size
#  done
#) &
#echo $! >"$script_pid_file"
