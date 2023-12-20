#!/bin/bash 

rm -rf "run.dpp-local-nc8_gl6-1.warmup.cfg"

job0_0=$(sbatch --job-name="info.before.dpp-local-nc8_gl6-1.warmup.cfg" -w gl6 -n 1 --dependency=afterany:43262 collect-info.before.sh | awk '{{print $NF}}')
job0_1=$(sbatch --job-name="dpp-local-nc8_gl6-1.warmup.cfg" -w gl6 -n 8 --dependency=afterany:$job0_0 haddock3 "dpp-local-nc8_gl6-1.warmup.cfg" | awk '{{print $NF}}')
job0_2=$(sbatch --job-name="info.after.dpp-local-nc8_gl6-1.warmup.cfg" -w gl6 -n 1 --dependency=afterany:$job0_1 collect-info.after.sh | awk '{{print $NF}}')
job1_0=$(sbatch --job-name="info.before.daa-local-nc8_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job0_2 collect-info.before.sh | awk '{{print $NF}}')
job1_1=$(sbatch --job-name="daa-local-nc8_gl6-11.cfg" -w gl6 -n 8 --dependency=afterany:$job1_0 haddock3 "daa-local-nc8_gl6-11.cfg" | awk '{{print $NF}}')
job1_2=$(sbatch --job-name="info.after.daa-local-nc8_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job1_1 collect-info.after.sh | awk '{{print $NF}}')
job2_0=$(sbatch --job-name="info.before.dpp-local-nc8_gl6-12.cfg" -w gl6 -n 1 --dependency=afterany:$job1_2 collect-info.before.sh | awk '{{print $NF}}')
job2_1=$(sbatch --job-name="dpp-local-nc8_gl6-12.cfg" -w gl6 -n 8 --dependency=afterany:$job2_0 haddock3 "dpp-local-nc8_gl6-12.cfg" | awk '{{print $NF}}')
job2_2=$(sbatch --job-name="info.after.dpp-local-nc8_gl6-12.cfg" -w gl6 -n 1 --dependency=afterany:$job2_1 collect-info.after.sh | awk '{{print $NF}}')
job3_0=$(sbatch --job-name="info.before.dpp-local-nc8_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job2_2 collect-info.before.sh | awk '{{print $NF}}')
job3_1=$(sbatch --job-name="dpp-local-nc8_gl6-11.cfg" -w gl6 -n 8 --dependency=afterany:$job3_0 haddock3 "dpp-local-nc8_gl6-11.cfg" | awk '{{print $NF}}')
job3_2=$(sbatch --job-name="info.after.dpp-local-nc8_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job3_1 collect-info.after.sh | awk '{{print $NF}}')
job4_0=$(sbatch --job-name="info.before.daa-local-nc4_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job3_2 collect-info.before.sh | awk '{{print $NF}}')
job4_1=$(sbatch --job-name="daa-local-nc4_gl6-11.cfg" -w gl6 -n 4 --dependency=afterany:$job4_0 haddock3 "daa-local-nc4_gl6-11.cfg" | awk '{{print $NF}}')
job4_2=$(sbatch --job-name="info.after.daa-local-nc4_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job4_1 collect-info.after.sh | awk '{{print $NF}}')
job5_0=$(sbatch --job-name="info.before.dpp-local-nc4_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job4_2 collect-info.before.sh | awk '{{print $NF}}')
job5_1=$(sbatch --job-name="dpp-local-nc4_gl6-11.cfg" -w gl6 -n 4 --dependency=afterany:$job5_0 haddock3 "dpp-local-nc4_gl6-11.cfg" | awk '{{print $NF}}')
job5_2=$(sbatch --job-name="info.after.dpp-local-nc4_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job5_1 collect-info.after.sh | awk '{{print $NF}}')
job6_0=$(sbatch --job-name="info.before.daa-local-nc8_gl6-12.cfg" -w gl6 -n 1 --dependency=afterany:$job5_2 collect-info.before.sh | awk '{{print $NF}}')
job6_1=$(sbatch --job-name="daa-local-nc8_gl6-12.cfg" -w gl6 -n 8 --dependency=afterany:$job6_0 haddock3 "daa-local-nc8_gl6-12.cfg" | awk '{{print $NF}}')
job6_2=$(sbatch --job-name="info.after.daa-local-nc8_gl6-12.cfg" -w gl6 -n 1 --dependency=afterany:$job6_1 collect-info.after.sh | awk '{{print $NF}}')
job7_0=$(sbatch --job-name="info.before.dpp-local-nc16_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job6_2 collect-info.before.sh | awk '{{print $NF}}')
job7_1=$(sbatch --job-name="dpp-local-nc16_gl6-11.cfg" -w gl6 -n 16 --dependency=afterany:$job7_0 haddock3 "dpp-local-nc16_gl6-11.cfg" | awk '{{print $NF}}')
job7_2=$(sbatch --job-name="info.after.dpp-local-nc16_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job7_1 collect-info.after.sh | awk '{{print $NF}}')
job8_0=$(sbatch --job-name="info.before.daa-local-nc8_gl6-13.cfg" -w gl6 -n 1 --dependency=afterany:$job7_2 collect-info.before.sh | awk '{{print $NF}}')
job8_1=$(sbatch --job-name="daa-local-nc8_gl6-13.cfg" -w gl6 -n 8 --dependency=afterany:$job8_0 haddock3 "daa-local-nc8_gl6-13.cfg" | awk '{{print $NF}}')
job8_2=$(sbatch --job-name="info.after.daa-local-nc8_gl6-13.cfg" -w gl6 -n 1 --dependency=afterany:$job8_1 collect-info.after.sh | awk '{{print $NF}}')
job9_0=$(sbatch --job-name="info.before.dpp-local-nc4_gl6-12.cfg" -w gl6 -n 1 --dependency=afterany:$job8_2 collect-info.before.sh | awk '{{print $NF}}')
job9_1=$(sbatch --job-name="dpp-local-nc4_gl6-12.cfg" -w gl6 -n 4 --dependency=afterany:$job9_0 haddock3 "dpp-local-nc4_gl6-12.cfg" | awk '{{print $NF}}')
job9_2=$(sbatch --job-name="info.after.dpp-local-nc4_gl6-12.cfg" -w gl6 -n 1 --dependency=afterany:$job9_1 collect-info.after.sh | awk '{{print $NF}}')
job10_0=$(sbatch --job-name="info.before.daa-local-nc8_gl6-14.cfg" -w gl6 -n 1 --dependency=afterany:$job9_2 collect-info.before.sh | awk '{{print $NF}}')
job10_1=$(sbatch --job-name="daa-local-nc8_gl6-14.cfg" -w gl6 -n 8 --dependency=afterany:$job10_0 haddock3 "daa-local-nc8_gl6-14.cfg" | awk '{{print $NF}}')
job10_2=$(sbatch --job-name="info.after.daa-local-nc8_gl6-14.cfg" -w gl6 -n 1 --dependency=afterany:$job10_1 collect-info.after.sh | awk '{{print $NF}}')
job11_0=$(sbatch --job-name="info.before.dpp-local-nc32_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job10_2 collect-info.before.sh | awk '{{print $NF}}')
job11_1=$(sbatch --job-name="dpp-local-nc32_gl6-11.cfg" -w gl6 -n 32 --dependency=afterany:$job11_0 haddock3 "dpp-local-nc32_gl6-11.cfg" | awk '{{print $NF}}')
job11_2=$(sbatch --job-name="info.after.dpp-local-nc32_gl6-11.cfg" -w gl6 -n 1 --dependency=afterany:$job11_1 collect-info.after.sh | awk '{{print $NF}}')
cat > check-local-exp-gl6_2.sh << EOF
#!/bin/bash
echo $job1_1,$job2_1,$job3_1,$job4_1,$job5_1,$job6_1,$job7_1,$job8_1,$job9_1,$job10_1,$job11_1
sacct -o jobid,jobname%50,cluster,Node,state,start,end,ConsumedEnergy,AveRSS,AveDiskRead,AveDiskWrite,AveVMSize,elapsed,NCPUS     -j $job1_1,$job2_1,$job3_1,$job4_1,$job5_1,$job6_1,$job7_1,$job8_1,$job9_1,$job10_1,$job11_1     > local-exp-gl6_2-data.txt
cat local-exp-gl6_2-data.txt
EOF
