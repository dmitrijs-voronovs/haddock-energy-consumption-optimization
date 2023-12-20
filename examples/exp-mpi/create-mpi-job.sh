#!/bin/bash

workflow=$1

filename="$workflow-mpi"
cfg_template="template/${filename}-template.cfg"
job_template="template/mpi-template.job"

cfg_template_ncores="___NCORES___"
cfg_template_nodes="___NODES___"
cfg_template_tasks_per_node="___TASKS_PER_NODE___"
cfg_template_run_dir="___RUNDIR___"
job_template_cinfing_file="___CONFIG_FILE___"

# script that accepts ncores, nodes, tasks_per_node as cli arguments and replaces them in template files

# get cli arguments
ncores=$2
nodes=$3
tasks_per_node=$4
node=$5
trial=$6
# optional argument for warmup flow
warmup=$7

#create cfg and job files with ncores in filename
concat_args="$filename-nc${ncores}-no${nodes}-tpn${tasks_per_node}_$node-$trial"
if [ -n "$warmup" ]; then
    concat_args="$concat_args.warmup"
fi

cfg_file="$concat_args.cfg"
job_file="$concat_args.job"
run_dir="run.$concat_args"

echo $cfg_template 
echo "filename: $cfg_file, jobname: $job_file, ncores: $ncores, nodes: $nodes, node: $node, tasks per node: $tasks_per_node, trial: $trial, run_dir: $run_dir"

# copy template files
cp "$cfg_template" "$cfg_file"
cp "$job_template" "$job_file"

# replace ncores in job file
sed -i "s/$cfg_template_nodes/$nodes/g" $job_file
sed -i "s/$cfg_template_tasks_per_node/$tasks_per_node/g" $job_file
sed -i "s/$job_template_cinfing_file/$cfg_file/g" $job_file

# replace ncores in cfg file
sed -i "s/$cfg_template_ncores/$ncores/g" $cfg_file
sed -i "s/$cfg_template_run_dir/$run_dir/g" $cfg_file