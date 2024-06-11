#!/bin/bash
# 
# Author: Tanmay Rajore
# 
# Copyright:
# 
# Copyright (c) 2024 Microsoft Research
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
