#!/bin/bash

exp_id=$1
command_pid_file="$exp_id-pid.txt"
script_pid_file="$exp_id-script_pid.txt"

kill_process() {
  local pid_file=$1
  echo "Killing the process with PID file: $pid_file"

  # Check if the PID file exists
  if [ -f "$pid_file" ]; then
      pid=$(cat "$pid_file")
      echo "PID file found with PID: $pid"
      if ps -p "$pid" > /dev/null; then
          echo "Killing script with PID: $pid"
          sudo kill "$pid"
      else
          echo "No active process found with PID: $pid"
      fi
      echo "removing file"
      sudo rm -f "$pid_file"
  else
      echo "PID file not found. No active process to kill."
  fi
  echo "done for $pid_file"
}

kill_process "$command_pid_file"
kill_process "$script_pid_file"