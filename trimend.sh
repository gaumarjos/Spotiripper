#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <filename.mp3> <seconds>"
    exit 1
fi

# Assign input parameters to variables
input_file="$1"
trim_seconds="$2"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found!"
    exit 1
fi

# Get the total duration of the input file in seconds
total_duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$input_file")

# Calculate the new duration by subtracting trim_seconds
new_duration=$(echo "$total_duration - $trim_seconds" | bc)

# Check if new duration is valid (greater than zero)
if (( $(echo "$new_duration <= 0" | bc -l) )); then
    echo "Error: Trimming $trim_seconds seconds exceeds total duration of the file."
    exit 1
fi

# Define output filename with "_trimmed" suffix
output_file="${input_file%.mp3}_trimmed.mp3"

# Trim the last specified seconds and create the new output file
ffmpeg -i "$input_file" -to "$new_duration" -c copy "$output_file"

echo "Trimmed file created: $output_file"