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
