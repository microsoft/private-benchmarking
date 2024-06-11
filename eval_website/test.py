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
import socket
import os

def receive_file(peer_ip, peer_port, file_name):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the address
        s.bind((peer_ip, peer_port))
        
        # Listen for incoming connections
        s.listen(1)
        
        print(f"Waiting for a connection from {peer_ip}:{peer_port}")
        
        # Accept a connection
        connection, client_address = s.accept()
        
        try:
            print(f"Connection established with {client_address}")
            
            # Receive the file data
            with open(file_name, 'wb') as file:
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    
            print("File received successfully.")
            
        finally:
            # Clean up the connection
            connection.close()

receive_file('127.0.0.1', 6300, 'received_file.txt')
