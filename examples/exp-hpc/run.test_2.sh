#!/bin/bash 

job0_0=$(sbatch --job-name="info.before.dpp-hpc-con10-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 collect-info.before.sh "run.dpp-hpc-con10-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job0_1=$(sbatch --job-name="dpp-hpc-con10-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 72 --dependency=afterany:$job0_0 haddock3 "dpp-hpc-con10-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job0_2=$(sbatch --job-name="info.after.dpp-hpc-con10-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job0_1 collect-info.after.sh "run.dpp-hpc-con10-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job1_0=$(sbatch --job-name="info.before.dpp-hpc-con1-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job0_2 collect-info.before.sh "run.dpp-hpc-con1-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job1_1=$(sbatch --job-name="dpp-hpc-con1-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 72 --dependency=afterany:$job1_0 haddock3 "dpp-hpc-con1-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job1_2=$(sbatch --job-name="info.after.dpp-hpc-con1-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job1_1 collect-info.after.sh "run.dpp-hpc-con1-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job2_0=$(sbatch --job-name="info.before.dpp-hpc-con10-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job1_2 collect-info.before.sh "run.dpp-hpc-con10-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job2_1=$(sbatch --job-name="dpp-hpc-con10-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 72 --dependency=afterany:$job2_0 haddock3 "dpp-hpc-con10-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job2_2=$(sbatch --job-name="info.after.dpp-hpc-con10-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job2_1 collect-info.after.sh "run.dpp-hpc-con10-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job3_0=$(sbatch --job-name="info.before.dpp-hpc-con5-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job2_2 collect-info.before.sh "run.dpp-hpc-con5-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job3_1=$(sbatch --job-name="dpp-hpc-con5-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 72 --dependency=afterany:$job3_0 haddock3 "dpp-hpc-con5-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job3_2=$(sbatch --job-name="info.after.dpp-hpc-con5-ql9_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job3_1 collect-info.after.sh "run.dpp-hpc-con5-ql9_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job4_0=$(sbatch --job-name="info.before.dpp-hpc-con1-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job3_2 collect-info.before.sh "run.dpp-hpc-con1-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job4_1=$(sbatch --job-name="dpp-hpc-con1-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 72 --dependency=afterany:$job4_0 haddock3 "dpp-hpc-con1-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job4_2=$(sbatch --job-name="info.after.dpp-hpc-con1-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job4_1 collect-info.after.sh "run.dpp-hpc-con1-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job5_0=$(sbatch --job-name="info.before.dpp-hpc-con5-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job4_2 collect-info.before.sh "run.dpp-hpc-con5-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job5_1=$(sbatch --job-name="dpp-hpc-con5-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 72 --dependency=afterany:$job5_0 haddock3 "dpp-hpc-con5-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
job5_2=$(sbatch --job-name="info.after.dpp-hpc-con5-ql18_gl2-gl5-gl6-11.cfg" -w GreenLab-STF,gl5,gl6 -n 3 --dependency=afterany:$job5_1 collect-info.after.sh "run.dpp-hpc-con5-ql18_gl2-gl5-gl6-11.cfg" | awk '{{print $NF}}')
cat > check.test_2.sh << EOF
#!/bin/bash
echo $job0_1,$job1_1,$job2_1,$job3_1,$job4_1,$job5_1
sacct -o jobid,jobname%60,cluster,Node%24,state,start,end,ConsumedEnergy,AveRSS,AveDiskRead,AveDiskWrite,AveVMSize,SystemCPU,UserCPU,AveCPU,elapsed,NCPUS     -j $job0_1,$job1_1,$job2_1,$job3_1,$job4_1,$job5_1     > data.test_2.txt
cat data.test_2.txt
EOF
