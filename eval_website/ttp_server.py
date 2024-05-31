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

# Define the directory where files will be stored
UPLOAD_DIR = 'uploads'

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get the length of the content
        content_length = int(self.headers['Content-Length'])

        # Read the raw HTTP POST data from the socket till all is received
        post_data = self.rfile.read(content_length)
        # Convert the raw data to a string
        post_data = post_data.decode('utf-8')
        # Find the boundary string
        parsed_data = json.loads(post_data)

        # Print the parsed data
        print(parsed_data)
        modelID = parsed_data['modelID']
        modelName = parsed_data['modelName']
        datasetID = parsed_data['datasetID']
        datasetName = parsed_data['datasetName']
        verification_code = parsed_data['verification_code']

        # Create the upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save the uploaded files
        ca_cert_file = parsed_data['ca_cert']
        server_cert_file = parsed_data['server_cert']
        server_key_file = parsed_data['server_key']

        ca_cert_path = os.path.join(UPLOAD_DIR, 'ca_cert.pem.enc')
        server_cert_path = os.path.join(UPLOAD_DIR, 'server_cert.pem.enc')
        server_key_path = os.path.join(UPLOAD_DIR, 'server_key.pem.enc')

        # Encrypt and save the uploaded files
        key = os.environ.get('ENCRYPTION_KEY').encode()  # Encryption key
        nonce = secrets.token_bytes(12)
        # Encrypt and save the uploaded files
        cipher = Cipher(algorithms.AES(key), modes.CBC(nonce))
        encryptor = cipher.encryptor() 
        with open(ca_cert_path, 'wb') as f:
            encrypted_data = encryptor.update(ca_cert_file.encode()) + encryptor.finalize()
            f.write(encrypted_data)

        with open(server_cert_path, 'wb') as f:
            encrypted_data = encryptor.update(server_cert_file.encode()) + encryptor.finalize()
            f.write(encrypted_data)

        with open(server_key_path, 'wb') as f:
            encrypted_data = encryptor.update(server_key_file.encode()) + encryptor.finalize()
            f.write(encrypted_data)

        # Respond with success message
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Metadata and files received successfully')

        # Call the function to run the Bash script
        evaluation_file_path = "./indicxnli.sh"
        #print(modelID,modelName,datasetID,datasetName,evaluation_file_path, verification_code, ca_cert_path, server_cert_path, server_key_path)
        #check if modelID is integer only
        if re.match("^[0-9]*$", modelID):
            modelID = int(modelID)
        if re.match("^[0-9]*$", datasetID):
            datasetID = int(datasetID)
        #check if model name is string only
        if re.match("^[a-zA-Z]*$", modelName):
            modelName = str(modelName)
        if re.match("^[a-zA-Z]*$", datasetName):
            datasetName = str(datasetName)
        #check verification code is hex only
        if re.match("^[0-9a-fA-F]*$", verification_code):
            verification_code = str(verification_code)

        run_bash_script(modelID, modelName, datasetID, datasetName, evaluation_file_path, verification_code, ca_cert_path, server_cert_path, server_key_path)

def run_bash_script(modelID,modelName,datasetID,datasetName,evaluation_file_path, verification_code, ca_cert_path, server_cert_path, server_key_path):
    # Command to execute the Bash script
    bash_command = f"./ttp_bash.sh {modelID} {modelName} {datasetID} {datasetName} {evaluation_file_path} {verification_code} {ca_cert_path} {server_cert_path} {server_key_path}"
    key = os.environ.get('ENCRYPTION_KEY').encode()  # Encryption key
    nonce = secrets.token_bytes(12)
        # Encrypt and save the uploaded files
    cipher = Cipher(algorithms.AES(key), modes.CBC(nonce))
    encryptor = cipher.encryptor() 
    #write the command to a file
    with open('ttp_bash.sh.enc', 'w') as f:
        encrypted_data = encryptor.update(bash_command.encode()) + encryptor.finalize()
        f.write(encrypted_data)

    # Decrypt the command
    with open('ttp_bash.sh.enc', 'rb') as f:
        encrypted_data = f.read()
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        bash_command = decrypted_data.decode()
    file_ex= bash_command
    # Execute the Bash script
    def execute(cmd):
        sanitized_cmd = shlex.quote(cmd)
        popen = subprocess.Popen(sanitized_cmd,shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line 
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

# Example

    for path in execute(file_ex):
        print(path, end="")


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
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=server_cert_file, keyfile=server_key_file)
    context.load_verify_locations(cafile=ca_cert_file)
    context.verify_mode = ssl.CERT_NONE
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()