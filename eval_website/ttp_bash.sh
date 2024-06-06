#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# Define the ports for listening
website_ip='10.168.241.37'
PORT_MODEL=7001
PORT_DATASET=7002
evaluation_file_path=$5
# Function to receive files

decrypt_the_certificates() {
    # Decrypt the server certificate
    openssl enc -d -aes-256-cbc -in server_cert.pem.enc -out server_cert.pem -k $ENCRYPTION_KEY

    # Decrypt the server private key
    openssl enc -d -aes-256-cbc -in server_key.pem.enc -out server_key.pem -k $ENCRYPTION_KEY

    # Decrypt the CA certificate
    openssl enc -d -aes-256-cbc -in ca_cert.pem.enc -out ca_cert.pem -k $ENCRYPTION_KEY
}

receive_file() {
    # Arguments: $1 = port, $2 = file save location

    # Create a temporary directory to store the received files
    temp_dir=$(mktemp -d)

    # Start Python script to receive files
    python3 - <<END
import socket
import ssl

def receive_file(port, file_path, server_cert, server_key):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', port))
        s.listen(1)
        print(f"Listening for files on port {port}...")
        conn, addr = s.accept()

        # Wrap the client socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        context.load_verify_locations(cafile="ca.crt")
        context.verify_mode = ssl.CERT_NONE
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(conn, server_side=True) as ssl_conn:
            print(f"Connected to {addr} via TLSv1.3")

            # Receive the file data
            with open(file_path, 'wb') as file:
                while True:
                    data = ssl_conn.recv(1024)
                    if not data:
                        break
                    file.write(data)

            print(f"File received and saved at {file_path}")

receive_file($1, "$2", "server.crt", "server.key")
END
}
decrypt_the_certificates
# Start receiving model files on PORT_MODEL
receive_file $PORT_MODEL "model.tar.gz" &

# Store the PID of the first background process
pid_model=$!

# Start receiving dataset files on PORT_DATASET
receive_file $PORT_DATASET "dataset.tar.gz" &

# Store the PID of the second background process
pid_dataset=$!

# Wait for both background processes to finish
wait $pid_model
wait $pid_dataset

# Both tasks have completed
echo "Both tasks have completed successfully."

# Extract the model and dataset files
tar -xzf model.tar.gz
tar -xzf dataset.tar.gz

# Run the model evaluation script
#evaluation_file_path=$1
#print all the input to the script
# for i in "$@"
# do
#     echo "Input: $i"
# done
$evaluation_file_path
path_to_test=./generate_results.py
# generate the evaluation report
echo "Running model accuracy tests..."
python3.10 $path_to_test > output_file.log
wait $!
echo "Model accuracy tests completed successfully."

log_file="output_file.log"
model_id=$1
model_name=$2
dataset_id=$3
dataset_name=$4

# Generate Python script
python_script=$(cat << END
import re
import argparse
import datetime
import requests

def extract_metrics(log_file):
    # Regular expressions to extract metrics
    accuracy_pattern = r'Accuracy: (\d+\.\d+)'
    precision_pattern = r'Precision: (\d+\.\d+)'
    recall_pattern = r'Recall: (\d+\.\d+)'
    f1_score_pattern = r'F1 Score: (\d+\.\d+)'

    # Initialize metrics
    accuracy = None
    precision = None
    recall = None
    f1_score = None

    # Read log file and extract metrics
    with open('$log_file', 'r') as f:
        log_content = f.read()
        accuracy_match = re.search(accuracy_pattern, log_content)
        if accuracy_match:
            accuracy = float(accuracy_match.group(1))

        precision_match = re.search(precision_pattern, log_content)
        if precision_match:
            precision = float(precision_match.group(1))

        recall_match = re.search(recall_pattern, log_content)
        if recall_match:
            recall = float(recall_match.group(1))

        f1_score_match = re.search(f1_score_pattern, log_content)
        if f1_score_match:
            f1_score = float(f1_score_match.group(1))

    return accuracy, precision, recall, f1_score

def main():
    # Extract metrics
    accuracy, precision, recall, f1_score = extract_metrics('$log_file')

    # Display metrics
    model_id=$model_id
    model_name="$model_name"
    owner_name="$owner_name"
    dataset_id=$dataset_id
    print("Model ID:", model_id)
    print("Model Name:", model_name)
    print("Owner Name:", owner_name)
    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1_score)
     # Send metrics to update_leaderboard view
    ttp_user_token = 'a8clt0lf6dgnuq3smh9ex7tpczpo8bw5'
    payload = {
        'model_id': model_id,
        'dataset_id': dataset_id,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
    }
    cookies = {
    'auth_token': ttp_user_token,
}

    response = requests.post('http://$website_ip:8000/leaderboard/update', data=payload, cookies=cookies)
    if response.status_code == 200:
        print("Leaderboard updated successfully")
    else:
        print("Error updating leaderboard:", response.text)

if __name__ == "__main__":
    main()
END
)

# Save Python script to a temporary file
python_script_file="/tmp/metrics_script.py"
echo "$python_script" > "$python_script_file"

# Execute Python script
python3 "$python_script_file" "$@"




