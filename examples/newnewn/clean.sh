#!/bin/bash

# Get a list of directories created more than 2 days ago and match the naming pattern
directories=$(find . -maxdepth 1 -type d -mtime +2 -name 'run.*' | grep -E '^\.\/run\.[^/.]+$')

# Loop through the directories and perform the cleaning
for dir in $directories; do
    if [ -d "$dir" ]; then  # Check if it's a directory
        echo "Cleaning directory: $dir"
        find "$dir" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +  # Clean all subdirectories
    else
        echo "Skipping non-directory: $dir"
    fi
done
