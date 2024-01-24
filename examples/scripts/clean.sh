#!/bin/bash

old_directories=$(find . -maxdepth 1 -type d -mtime +3 -name 'run.*' | grep -E '^\.\/run\..+$')
rm -rf $old_directories

run_directories=$(find . -maxdepth 1 -type d -mtime +1 -name 'run.*' | grep -E '^\.\/run\.[^/.]+$')

# Loop through the directories and perform the cleaning of run-specific files
for dir in $run_directories; do
    if [ -d "$dir" ]; then  # Check if it's a directory
        echo "Cleaning directory: $dir"
        find "$dir" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +  # Clean all subdirectories
    else
        echo "Skipping non-directory: $dir"
    fi
done



