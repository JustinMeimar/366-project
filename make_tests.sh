#!/bin/bash
for ((i=1; i<=$1; i++))
do
    echo "Generating test #$i"
    file_name="fuzz_test_${i}.in"
    python3 fuzzer.py "fuzz_tests/$file_name"
done
