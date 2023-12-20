#!/bin/bash

workflow=$1

filename="$workflow-hpc"
cfg_template="template/${filename}-template.cfg"

cfg_template_concat="___CONCAT___"
cfg_template_queue_limit="___QUEUE_LIMIT___"
cfg_template_run_dir="___RUNDIR___"

# script that accepts ncores, nodes, tasks_per_node as cli arguments and replaces them in template files

# get cli arguments
concat=$2
queue_limit=$3
node=$4
trial=$5
# optional argument for warmup flow
warmup=$6

#create cfg and job files with ncores in filename
concat_args="$filename-con${concat}-ql${queue_limit}_$node-$trial"
if [ -n "$warmup" ]; then
    concat_args="$concat_args.warmup"
fi
cfg_file="$concat_args.cfg"
run_dir="run.$concat_args"

echo $cfg_template 
echo "filename: $cfg_file, concat: $concat, queue_limit: $queue_limit, node: $node, trial: $trial, run_dir: $run_dir"

# copy template files
cp "$cfg_template" "$cfg_file"

# replace ncores in cfg file
sed -i "s/$cfg_template_concat/$concat/g" $cfg_file
sed -i "s/$cfg_template_queue_limit/$queue_limit/g" $cfg_file
sed -i "s/$cfg_template_run_dir/$run_dir/g" $cfg_file