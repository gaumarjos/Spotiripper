#!/bin/bash

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <arg1> [arg2]"
    exit 1
fi

# Assign arguments to variables
arg1=$1
arg2=${2:-""}

cd ~/PycharmProjects/Spotiripper/
python main.py $arg1 $arg2
