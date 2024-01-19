#!/bin/bash

rundir=$1
infodir="$rundir.info"
mkdir $infodir

echo "Cooling down for 5 minutes..."
sleep $((5*60))

scontrol show nodes > $infodir/nodes_info.before.txt
ps aux > $infodir/proc_info.before.txt

echo "Collecting info for $rundir (before run) done. Ready to run."