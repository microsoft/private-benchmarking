#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
function print_help {
    echo "Usage: $0 --batch_size BATCH_SIZE --n_embd N_EMBD --path PATH"
    echo ""
    echo "Arguments:"
    echo "  --batch_size  Number of data points to consider."
    echo "  --n_embd      Number of embedding dimensions."
    echo "  --path        Path to the directory containing the datapoints."
    exit 1
}

function get_n_seq {
    local filename="$1"
    local n_embd="$2"

    # Get file size in bytes
    local n_elements=$(stat -c %s "$filename")

    # Check if n_elements is divisible by (4 * n_embd)
    if (( n_elements % (4 * n_embd) != 0 )); then
        echo "Error: n_elements not divisible by (4 * n_embd)"
        exit 1
    fi

    echo $((n_elements / (4 * n_embd)))
}

# Default values
batch=""
path=""
n_embd=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --batch_size)
        batch="$2"
        shift # past argument
        shift # past value
        ;;
        --n_embd)
        n_embd="$2"
        shift # past argument
        shift # past value
        ;;
        --path)
        path="$2"
        shift # past argument
        shift # past value
        ;;
        *)
        # Unknown option
        shift # past argument
        ;;
    esac
done

# Check if all arguments are provided
if [[ -z "$batch" || -z "$n_embd" || -z "$path" ]]; then
    print_help
fi

# Metadata file to write n_seq
filename="metadata.txt"

# Ensure file is empty before writing to it
> "$filename"

# Process each data point
for ((i=0; i<batch; i++)); do
    data_filename="${path}${i}.dat"
    echo "filename: $data_filename"
    n_seq=$(get_n_seq "$data_filename" "$n_embd")
    echo "$n_seq" >> "$filename"
done

echo "Metadata written to $filename"
