#!/bin/bash

rundir=$1
infodir="$rundir.info"

kill "$(cat $infodir/pid.proc_utilization.txt)"
kill "$(cat $infodir/pid.mem_utilization.txt)"
kill "$(cat $infodir/pid.cpu_frequency.txt)"

scontrol show nodes > $infodir/nodes_info.after.txt
ps aux > $infodir/proc_info.after.txt

echo "Collecting info for $rundir (after run) done."