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

"""
This script sends the keys to the server.
Usage:
python3 send_keys.py dataset {id} {dataset_ip_received} {dataset_port_received}
python3 send_keys.py model {id} {model_ip_received} {model_port_received}

"""

import socket
import ssl
import os
import argparse
from tqdm import tqdm
import glob


def send_file(folder_path, server_address, server_port, ca, type,model_name,dataset_id):
    # Check if the file exists
    # try:
    #     with open(file_path, "rb") as file:
    #         file_data = file.read()
    # except FileNotFoundError:
    #     print(f"File not found: {file_path}")
    #     return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False

        with context.wrap_socket(
            s, server_side=False, server_hostname=server_address
        ) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {server_address}:{server_port}")
                # send the folder
                ssl_socket.sendall(folder_path.encode())
                # iterate over the folder and send the number of files
                dataset_keys = glob.glob(os.path.join(folder_path, ""))
                dataset_keys = sorted([x.split("/")[-1] for x in dataset_keys])
                print(dataset_keys)
                model_keys = glob.glob(os.path.join(folder_path, ""))
                # only keep the file name and sort them
                model_keys = sorted([x.split("/")[-1] for x in model_keys])
                print(model_keys)
                if type == "dataset":
                    num_files = len(dataset_keys)
                    folder = dataset_keys
                elif type == "model":
                    num_files = len(model_keys)
                    folder = model_keys
                else:
                    print('Invalid type. Use "dataset" or "model"')
                    exit(1)

                ssl_socket.sendall(str(num_files).encode())
                print(f"Sending {num_files} files")
                # iterate over the folder and send the files

                for file_name in tqdm(folder):
                    file_path = os.path.join(folder_path, file_name)
                    # Send the file name
                    ssl_socket.sendall(file_name.encode())

                    # Send the file size
                    file_size = os.path.getsize(file_path)
                    ssl_socket.sendall(str(file_size).encode())

                    # Send the file data
                    with open(file_path, "rb") as f:
                        while True:
                            file_data = f.read(1024)
                            if not file_data:
                                break
                            ssl_socket.sendall(file_data)
                    # Send end of file delimiter
                    # ssl_socket.sendall(b"EOF")
                    # Receive confirmation
                    confirmation = ssl_socket.recv(1024).decode()
                    print(f"Sent {file_name}: {confirmation}")

                print("Folder sent successfully")
            except ConnectionRefusedError:
                print(f"Connection refused: {server_address}:{server_port}")
            except ssl.SSLError as e:
                print(f"SSL Error: {e}")
            except Exception as e:
                print(f"Error: {e}")


# Usage example
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send keys")
    parser.add_argument(
        "type", type=str, help="Type of keys to send (dataset or model)"
    )
    parser.add_argument("id", type=str, help="Max number of iterations")
    parser.add_argument("server_address", type=str, help="Server address")
    parser.add_argument("server_port", type=int, help="Server port")
    parser.add_argument("model_name", type=str, help="Model name")
    parser.add_argument("dataset_id", type=str, help="Dataset id")
    args = parser.parse_args()
    print(
        f"Sending keys of type {args.type} with id {args.id} to {args.server_address}:{args.server_port}"
    )


    for i in range(int(args.id) + 1):
        if args.type == "dataset":
            folder_path = f"./ezpc_keys/{args.model_name}_{args.dataset_id}_{i}/offline_client/"
        elif args.type == "model":
            folder_path = f"./ezpc_keys/{args.model_name}_{args.dataset_id}_{i}/offline_server/"
        else:
            print('Invalid type. Use "dataset" or "model"')
            exit(1)
        send_file(
            folder_path,
            args.server_address,
            args.server_port,
            "ca.crt",
            args.type,
            args.model_name,
            args.dataset_id,
        )