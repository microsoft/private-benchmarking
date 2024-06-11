# TTP/TEE Util scripts

This folder contains scripts for receiving model and dataset files, evaluating the model, and updating the leaderboard with the evaluation metrics. 

These scripts are intended to be used by the Trusted Third Party (TTP) and Trusted Execution Environment (TEE) party setup.

## Files

1. `ttp_bash.sh`: This is a bash script that receives model and dataset files over a network, decrypts certificates, evaluates the model, and updates the leaderboard with the evaluation metrics.

2. `generate_results.py`: This is a Python script that calculates and prints the accuracy, precision, recall, and F1 score of the model predictions.

## Usage

### ttp_bash.sh

This script is designed to be run on a server that is set up to receive files over a network. It listens on two ports for incoming connections, one for the model file and one for the dataset file. The files are received over a secure TLS connection.

The script then decrypts the server certificate, server private key, and CA certificate using OpenSSL.

After receiving the files, the script extracts the model and dataset files and runs the model evaluation script.

The script then generates a Python script to extract the evaluation metrics from the log file and send them to the leaderboard update view.

### generate_results.py

This script takes as input a file of ground truth labels and a file of predicted labels. It calculates the accuracy, precision, recall, and F1 score of the predictions and prints these metrics.

The script is designed to be run as a standalone program, with the input files specified as command-line arguments.

## Requirements

- Python 3.10
- OpenSSL
- Bash shell
- sklearn library for Python

## License

This project is licensed under the MIT License. See the individual Python files for the full license text.
