#!/bin/bash 

rm -rf "run.dpp-local-nc32_gl6-20.warmup.cfg"

job0_0=$(sbatch --job-name="info.before.dpp-local-nc32_gl6-20.warmup.cfg" -w gl6 -n 1 collect-info.before.sh | awk '{{print $NF}}')
job0_1=$(sbatch --job-name="dpp-local-nc32_gl6-20.warmup.cfg" -w gl6 -n 32 --dependency=afterany:$job0_0 haddock3 "dpp-local-nc32_gl6-20.warmup.cfg" | awk '{{print $NF}}')
job0_2=$(sbatch --job-name="info.after.dpp-local-nc32_gl6-20.warmup.cfg" -w gl6 -n 1 --dependency=afterany:$job0_1 collect-info.after.sh | awk '{{print $NF}}')
job1_0=$(sbatch --job-name="info.before.dpp-local-nc4_gl6-20.cfg" -w gl6 -n 1 --dependency=afterany:$job0_2 collect-info.before.sh | awk '{{print $NF}}')
job1_1=$(sbatch --job-name="dpp-local-nc4_gl6-20.cfg" -w gl6 -n 4 --dependency=afterany:$job1_0 haddock3 "dpp-local-nc4_gl6-20.cfg" | awk '{{print $NF}}')
job1_2=$(sbatch --job-name="info.after.dpp-local-nc4_gl6-20.cfg" -w gl6 -n 1 --dependency=afterany:$job1_1 collect-info.after.sh | awk '{{print $NF}}')
job2_0=$(sbatch --job-name="info.before.daa-local-nc4_gl6-20.cfg" -w gl6 -n 1 --dependency=afterany:$job1_2 collect-info.before.sh | awk '{{print $NF}}')
job2_1=$(sbatch --job-name="daa-local-nc4_gl6-20.cfg" -w gl6 -n 4 --dependency=afterany:$job2_0 haddock3 "daa-local-nc4_gl6-20.cfg" | awk '{{print $NF}}')
job2_2=$(sbatch --job-name="info.after.daa-local-nc4_gl6-20.cfg" -w gl6 -n 1 --dependency=afterany:$job2_1 collect-info.after.sh | awk '{{print $NF}}')
cat > check-local-exp-gl6_3.sh << EOF
#!/bin/bash
echo $job1_1,$job2_1
sacct -o jobid,jobname%50,cluster,Node,state,start,end,ConsumedEnergy,AveRSS,AveDiskRead,AveDiskWrite,AveVMSize,elapsed,NCPUS     -j $job1_1,$job2_1     > local-exp-gl6_3-data.txt
cat local-exp-gl6_3-data.txt
EOF
