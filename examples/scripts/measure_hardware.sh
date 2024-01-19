rundir=$1
infodir="$rundir.info"

interval=5

echo "Start hardware data collection"

nohup sar -P ALL $interval > $infodir/proc_utilization.log 2>&1 &
echo $! > $infodir/pid.proc_utilization.txt

nohup sar -r ALL $interval > $infodir/mem_utilization.log 2>&1 &
echo $! > $infodir/pid.mem_utilization.txt

nohup sh -c "while true; do echo \"\$(date)\n\$(cat /proc/cpuinfo | grep MHz)\"; sleep $interval; done" > $infodir/cpu_frequency.log 2>&1 &
echo $! > $infodir/pid.cpu_frequency.txt

