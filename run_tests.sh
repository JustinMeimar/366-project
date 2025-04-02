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

# Run greedy
for test_file in "$1"/*
do
    if [ -f "$test_file" ]; then
        echo "Running test: $test_file"
        python3 src/main.py "$test_file" greedy
    fi
done

# Run backtracking
for test_file in "$1"/*
do
    if [ -f "$test_file" ]; then
        echo "Running test: $test_file"
        python3 src/main.py "$test_file" backtracking 
    fi
done

