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
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import os, subprocess,re
from urllib.parse import parse_qs
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import json
import shlex
from cryptography.hazmat.backends import default_backend
import warnings
warnings.filterwarnings("ignore")

# Define the directory where files will be stored
UPLOAD_DIR = 'uploads'
working_directory = os.getcwd()

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        
        #receive the metadata
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        metadata = json.loads(post_data.decode('utf-8'))
        print(f'Metadata received: {metadata}')
        # Extract metadata
        modelID = metadata['modelID']
        modelName = metadata['modelName']
        datasetID = metadata['datasetID']
        datasetName = metadata['datasetName']
        verification_code = metadata['verification_code']

        # Respond with success message
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Metadata and files received successfully')

        # Call the function to run the Bash script
        #ask the user for input of the evaluation file path
        evaluation_file_path = "../eval.py"

        #print(modelID,modelName,datasetID,datasetName,evaluation_file_path, verification_code, ca_cert_path, server_cert_path, server_key_path)
        #check if modelID is integer only
        if type(modelID) != int:
            print("Invalid model ID")
            return
        #check if datasetID is integer only
        if type(datasetID) != int:
            print("Invalid dataset ID")
            return
        #check if verification code is str only
        if type(verification_code) != str:
            print("Invalid verification code")
            return
        #check if evaluation file path is valid
        if not os.path.exists(evaluation_file_path):
            print("Invalid evaluation file path")
            return
        #check if server certificate file path is valid
        server_cert_path = os.getcwd()+"/server.crt"
        print(server_cert_path)
        if not os.path.exists(server_cert_path):
            print("Invalid server certificate file path")
            return
        #check if server private key file path is valid
        server_key_path = os.getcwd()+"/server.key"
        if not os.path.exists(server_key_path):
            print("Invalid server private key file path")
            return
        #check if CA certificate file path is valid
        ca_cert_path = os.getcwd()+"/ca.crt"
        if not os.path.exists(ca_cert_path):
            print("Invalid CA certificate file path")
            return
        #call the function to run the bash script

        run_bash_script(modelID, modelName, datasetID, datasetName, evaluation_file_path, verification_code, ca_cert_path, server_cert_path, server_key_path)

def run_bash_script(modelID,modelName,datasetID,datasetName,evaluation_file_path, verification_code, ca_cert_path, server_cert_path, server_key_path):
    # Command to execute the Bash script
    bash_command = f"{working_directory}/ttp_bash.sh {modelID} {modelName} {datasetID} {datasetName} {evaluation_file_path} {verification_code} {ca_cert_path} {server_cert_path} {server_key_path}"
    BLOCK_SIZE = 16  # AES block size in bytes

# Function to pad the data to be encrypted
    def pad_data(data):
        padding_length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
        padding = bytes([padding_length]) * padding_length
        return data + padding

    # Function to remove padding after decryption
    def unpad_data(data):
        padding_length = data[-1]
        return data[:-padding_length]
        
    key = os.environ.get('ENCRYPTION_KEY')# Encryption key
    key = bytes.fromhex(key)
    nonce = secrets.token_bytes(16)
        # Encrypt and save the uploaded files
    cipher = Cipher(algorithms.AES(key), modes.CBC(nonce), backend=default_backend())
    encryptor = cipher.encryptor() 
    #write the command to a file
    with open('ttp_bash.sh.enc', 'wb') as f:
        padded=pad_data(bash_command.encode())
        encrypted_data = encryptor.update(padded) + encryptor.finalize()
        f.write(encrypted_data)

    # Decrypt the command
    with open('ttp_bash.sh.enc', 'rb') as f:
        encrypted_data = f.read()
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        bash_command = unpad_data(decrypted_data).decode()
    file_ex= bash_command
    # Execute the Bash script
    def execute(cmd):
        sanitized_cmd = shlex.quote(cmd)
        popen = subprocess.Popen(bash_command,shell=True, stdout=subprocess.PIPE, universal_newlines=True,cwd=working_directory)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line 
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

# Example

    for path in execute(file_ex):
        print(path.strip(), end="")

    print("Evaluation Completed Successfully , Leaderboard Updated")
    # Print the output and error messages
    # print("Bash script output:", stdout.decode('utf-8'))
    # print("Bash script errors:", stderr.decode('utf-8'))

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    
    # Load server certificate and private key
    ca_cert_file = 'ca.crt'
    server_cert_file = 'server.crt'
    server_key_file = 'server.key'
    #ask the user for input of the server certificate and private key file path and give option to use default
    server_cert_file = input("Enter the server certificate file path: ")
    server_key_file = input("Enter the server private key file path: ")
    ca_cert_file = input("Enter the CA certificate file path: ")
    if server_cert_file == "":
        server_cert_file = 'server.crt'
    if server_key_file == "":
        server_key_file = 'server.key'
    if ca_cert_file == "":
        ca_cert_file = 'ca.crt'

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=server_cert_file, keyfile=server_key_file)
    context.load_verify_locations(cafile=ca_cert_file)
    context.verify_mode = ssl.CERT_NONE
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    #remove host name check
    context.check_hostname = False

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()