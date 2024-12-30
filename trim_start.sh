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

# Check if trim_seconds is valid (not greater than total duration)
if (( $(echo "$trim_seconds >= $total_duration" | bc -l) )); then
    echo "Error: Trimming $trim_seconds seconds exceeds or equals total duration of the file."
    exit 1
fi

# Rename input file. The output file will have the same name as the input file.
renamed_input_file="${input_file%.mp3}_old.mp3"
mv "$input_file" "$renamed_input_file"

# Trim the specified seconds from the beginning and create the new output file (which is named "input_file")
ffmpeg -ss "$trim_seconds" -i "$renamed_input_file" -c copy "$input_file"

echo "Trimmed file created: $input_file, original renamed: $renamed_input_file"