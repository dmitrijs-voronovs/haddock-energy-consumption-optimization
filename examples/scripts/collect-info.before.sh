#!/bin/bash

rundir=$1
infodir="$rundir.info"
mkdir $infodir

interval=5

nohup sar -P ALL $interval > $infodir/proc_utilization.log 2>&1 &
echo $! > $infodir/pid.proc_utilization.txt

nohup sar -r $interval > $infodir/mem_utilization.log 2>&1 &
echo $! > $infodir/pid.mem_utilization.txt

nohup watch -n $interval 'cat /proc/cpuinfo | grep MHz' > $infodir/cpu_frequency.log 2>&1 &
echo $! > $infodir/pid.cpu_frequency.txt

echo "Cooling down for 5 minutes..."
sleep 20

scontrol show nodes > $infodir/nodes_info.before.txt
ps aux > $infodir/proc_info.before.txt

echo "Collecting info for $rundir (before run) done. Ready to run."