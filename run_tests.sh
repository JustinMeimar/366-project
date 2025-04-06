#!/bin/bash
# Check if a directory path is provided
if [ -z "$1" ]; then
    echo "Please provide a directory path as an argument"
    exit 1
fi
# Check if the path exists and is a directory
if [ ! -d "$1" ]; then
    echo "Error: '$1' is not a valid directory"
    exit 1
fi

# Initialize counter
counter=0

# Run greedy
for test_file in "$1"/*
do
    if [ -f "$test_file" ]; then
        echo "Running test: $test_file"
        python3 src/main.py "$test_file" greedy\
                    --viz "plots/greedy-${counter}.png"\
                    --benchmark "bench.csv"
        
        python3 src/main.py "$test_file" backtracking\
                    --viz "plots/backtracking-${counter}.png"\
                    --benchmark "bench.csv"

        ((counter++))
    fi
done
