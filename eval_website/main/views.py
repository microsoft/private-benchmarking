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
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate,logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ModelArchitectureForm
from .models import ModelArchitecture
from .forms import DatasetForm
from .models import Dataset
from .models import Evaluation
from .models import TrustedThirdParty,EzPCMetadata,confidential_compute
from django.contrib.auth.models import User
from django.urls import reverse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .forms import EvaluationForm
from django.shortcuts import get_object_or_404
from .models import LeaderboardEntry
from django.views.decorators.http import require_POST
import os,tempfile,zipfile,subprocess
from django.conf import settings
import shutil,ssl,requests,socket,uuid,json
from dotenv import load_dotenv

load_dotenv()
website_ip = settings.WEBSITE_IP
def homepage(request):
    models = ModelArchitecture.objects.all()
    datasets = Dataset.objects.all()
    return render(request, 'main/home.html', {"models": models, "datasets": datasets})

def register_request(request):
	if request.user.is_authenticated:
		return redirect("main:homepage")
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("main:homepage")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="main/register.html", context={"register_form":form})


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("main:dashboard")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="main/login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("main:homepage")

def evaluation_architecture_details(request, architecture_id):
    # Assuming architecture_id is passed as a parameter indicating the specific model architecture
    return render(request, 'main/architecture.html', {'architecture_id': architecture_id})
    
@login_required
def login_redirect(request):
    return render(request, 'main/login_redirect.html')

@login_required
def options(request):
    return render(request, 'main/options.html')

@login_required
def add_model_architecture(request):
    if request.method == 'POST':
        form = ModelArchitectureForm(request.POST,request.FILES)
        if form.is_valid():
            model_architecture = form.save(commit=False)
            model_architecture.user = request.user
            model_architecture.save()
            return redirect('main:options')
    else:
        form = ModelArchitectureForm()
    return render(request, 'main/add_model_architecture.html', {'form': form})
@login_required
def add_dataset(request):
    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.user = request.user
            dataset.save()
            return redirect('main:options')
    else:
        form = DatasetForm()
    return render(request, 'main/add_dataset.html', {'form': form})


@login_required
def dashboard(request):
    models = ModelArchitecture.objects.all()
    datasets= Dataset.objects.all()
    evaluation_requests = Evaluation.objects.all()
    print(evaluation_requests)
    return render(request, 'main/dashboard.html', {"user": request.user, "models": models, "datasets":datasets,"evaluation_requests": evaluation_requests})

@login_required
def model_detail(request, model_id):
    model_detail = ModelArchitecture.objects.get(pk=model_id)
    file_contents = ""
    try:
        with open(model_detail.architecture_file.path, 'r') as file:
            file_contents = file.read()
    except Exception as e:
        file_contents = f"Error reading file: {e}"
    return render(request, 'main/model_detail.html', {'model': model_detail, 'file_contents': file_contents})

@login_required
def dataset_detail(request, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    file_contents = ""
    try:
        with open(dataset.dataset_metadata.path, 'r') as file:
            file_contents = file.read()
    except Exception as e:
        file_contents = f"Error reading file: {e}"
    return render(request, 'main/dataset_detail.html', {"user":request.user, "dataset": dataset, 'file_contents': file_contents})

@login_required
def evaluate_model(request, model_id):
    model = get_object_or_404(ModelArchitecture, pk=model_id)
    return render(request, 'main/evaluate_model.html', {'model_id': model_id, 'model': model, 'datasets': Dataset.objects.all()})


@login_required
def send_request(request, model_id):
    print("Inside send_request view")  # Debugging output

    model = get_object_or_404(ModelArchitecture, pk=model_id)
    if request.method == 'POST':
        print("Received AJAX POST request")  # Debugging output

        try:
            data = json.loads(request.body)
            form = EvaluationForm(data)
            if form.is_valid():
                print("Form is valid")  # Debugging output

                dataset_id = form.cleaned_data['dataset'].id
                ip_address = form.cleaned_data['ip_address']
                port = form.cleaned_data['port']
                architecture_choosen = form.cleaned_data['architecture_choosen']
                if request.user == model.user:
                    is_approved_by_model_owner = True
                else:
                    is_approved_by_model_owner = False
                    

                print("Creating evaluation request")  # Debugging output
                Evaluation.objects.create(
                    user=request.user,
                    model=model,
                    dataset_id=dataset_id,
                    ip_address=ip_address,
                    port=port,
                    status='Pending',
                    is_approved_by_model_owner=is_approved_by_model_owner,
                    is_approved_by_dataset_owner=False,
                    architecture_choosen=architecture_choosen
                )

                return JsonResponse({'message': 'Evaluation request submitted successfully.'}, status=200)
            else:
                print("Form validation failed")  # Debugging output
                return JsonResponse({'error': 'Invalid form data.'}, status=400)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)  # Debugging output
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print("Error:", e)  # Debugging output
            return JsonResponse({'error :Internal Server Error'}, status=500)
    else:
        print("Not an AJAX POST request")  # Debugging output
        form = EvaluationForm()
    return render(request, 'main/evaluate_model.html', {'model': model, 'form': form, 'datasets': Dataset.objects.all()})

@login_required
def user_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    models = ModelArchitecture.objects.filter(user=user)
    datasets = Dataset.objects.filter(user=user)
    evaluations = Evaluation.objects.filter(user=user)
    return render(request, 'main/user_profile.html', {'user': user, 'models': models, 'datasets': datasets, 'evaluations': evaluations})

# Function to generate CA certificate
def generate_ca_certificate(ca_cert_path):
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', 'ca.key',
        '-out', 'ca.crt', '-days', '365', '-subj', '/CN=PrivateBenchmarking','-nodes'
    ], check=True)

    # Move CA certificate to specified path
    os.rename('ca.crt', ca_cert_path)

# Function to generate server certificate signed by CA
def generate_server_certificate(server_cert_path, server_key_path, ca_cert_path):
    subprocess.run([
        'openssl', 'req', '-newkey', 'rsa:2048', '-nodes', '-keyout', server_key_path,
        '-out', 'server.csr', '-subj', '/CN=PrivateBencharkming'
    ], check=True)

    subprocess.run([
        'openssl', 'x509', '-req', '-in', 'server.csr', '-CA', ca_cert_path,
        '-CAkey', 'ca.key', '-CAcreateserial', '-out', server_cert_path, '-days', '365'
    ], check=True)


    # Move server certificate and key to specified paths
    os.rename('server.crt', server_cert_path)
    os.rename('server.key', server_key_path)

def send_metadata_to_third_party(model, dataset, evaluation_request, ip_address, port, code,temp_ca_cert_path, temp_server_cert_path, temp_server_key_path):
    # Generate script content with runtime input parameters
    # Send metadata to third party
    data = {
        'modelID': model.id,
        'modelName': model.name,
        'datasetID': dataset.id,
        'datasetName': dataset.name,
        'evaluation_request': evaluation_request.id,
        'verification_code': code,
        
    }

    # Convert data to JSON format
    json_data = json.dumps(data)

    # Construct the URL for the third party server
    url = f"https://{ip_address}:{port}"

    # Prepare the files to send (if any)
    files = {
        'ca_cert': open(temp_ca_cert_path, 'rb'),
        'server_cert': open(temp_server_cert_path, 'rb'),
        'server_key': open(temp_server_key_path, 'rb')
        
    }

    # Configure SSL context with TLSv1.3
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="ca.crt")
    context.verify_mode = ssl.CERT_REQUIRED 
    context.check_hostname = False
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Send a POST request to the third party server
    response = requests.post(url, json=json_data, files=files, verify="ca.crt", timeout=10, stream=True)  # Set verify=False to disable SSL certificate verification

    # Check response
    if response.status_code == 200:
        print("Metadata sent successfully.")
    else:
        print("Failed to send metadata:", response.text)
def send_metadata_to_cc(model, dataset, evaluation_request, ip_address, port, code,temp_ca_cert_path, temp_server_cert_path, temp_server_key_path):
    # Generate script content with runtime input parameters
    # Send metadata to third party
    print("Sending metadata to confidential compute server")
    modelID=model.id
    modelName=model.name
    datasetID=dataset.id
    datasetName=dataset.name
    evaluation_requestID=evaluation_request.id
    verification_code=code
    print(modelID,modelName,datasetID,datasetName,evaluation_requestID,verification_code)

    data = {
        'modelID': modelID,
        'modelName': modelName,
        'datasetID': datasetID,
        'datasetName': datasetName,
        'evaluation_request': evaluation_requestID,
        'verification_code': verification_code,
        
    }

    # Convert data to JSON format
    json_data = json.dumps(data)

    # Construct the URL for the third party server
    url = f"https://{ip_address}:{port}"

    # Prepare the files to send (if any)
    files = {
        'ca_cert': open(temp_ca_cert_path, 'rb'),
        'server_cert': open(temp_server_cert_path, 'rb'),
        'server_key': open(temp_server_key_path, 'rb')
        
    }

    # Configure SSL context with TLSv1.3
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="ca.crt")
    context.verify_mode = ssl.CERT_REQUIRED 
    context.check_hostname = False
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Send a POST request to the third party server
    response = requests.post(url, json=json_data, files=files, verify="ca.crt", timeout=10, stream=True)  # Set verify=False to disable SSL certificate verification

    # Check response
    if response.status_code == 200:
        print("Metadata sent successfully.")
    else:
        print("Failed to send metadata:", response.text)

@login_required
def download_script(request, request_id):

    evaluation_request = get_object_or_404(Evaluation, id=request_id)
    model=evaluation_request.model
    dataset=evaluation_request.dataset
    architecture_choosen=evaluation_request.architecture_choosen
    if model.docker_file:
         docker_file_path = model.docker_file.path
    else:
         docker_file_path = None
    Auth_token = request.COOKIES['sessionid']
    csrf_token = request.COOKIES['csrftoken']

    ca_cert_path = os.path.join(settings.BASE_DIR, 'ca.crt')
    ca_key_path = os.path.join(settings.BASE_DIR, 'ca.key')

    if not os.path.exists(ca_cert_path) and not os.path.exists(ca_key_path):
        generate_ca_certificate(ca_cert_path)
    
    
    server_cert_path = os.path.join(settings.BASE_DIR, 'server.crt')
    server_key_path = os.path.join(settings.BASE_DIR, 'server.key')
    generate_server_certificate(server_cert_path, server_key_path, ca_cert_path)
    temp_dir = tempfile.mkdtemp()
    #move generated metadata file to the temp directory
    metadata_file_path = os.path.join(settings.BASE_DIR,'generate_metadata.sh')
    generate_results_file_path = os.path.join(settings.BASE_DIR,'generate_results.py')
    # Move certificates to temporary directory
    temp_ca_cert_path = os.path.join(temp_dir, 'ca.crt')
    temp_server_cert_path = os.path.join(temp_dir, 'server.crt')
    temp_server_key_path = os.path.join(temp_dir, 'server.key')
    shutil.copy(ca_cert_path, temp_ca_cert_path)
    shutil.move(server_cert_path, temp_server_cert_path)
    shutil.move(server_key_path, temp_server_key_path)

    

    if (evaluation_request.is_approved_by_model_owner and evaluation_request.is_approved_by_dataset_owner and architecture_choosen==1):
        # Generate script content with runtime input parameters
        script_content = '''#!/bin/bash'''
        if request.user == evaluation_request.dataset.user:
            script_content += f'''
# Check if the number of arguments is correct
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <folder_path> <ip_address> <port> <path_to_test>"
    exit 1
fi

# Extract arguments
folder_path=$1
ip_address=$2
port=$3
path_to_test=$4

start_time_full=$(date +%s.%N)
# Create a temporary directory to store the archive
temp_dir=$(mktemp -d)
wait $!
archive_name="data1.tar.gz"

# Create a tar archive of the folder
echo "Creating a tar archive of the folder..."
tar -czf "$temp_dir/$archive_name" -C "$folder_path" .
wait $!
# Script section for dataset transfer
echo "Transferring dataset folder..."
echo "Transferring dataset folder to model owner..."
send_file(){{

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
python3 - <<END
import socket
import ssl

def send_file(file_path, server_address, server_port, ca):
    # Check if the file exists
    # try:
    #     with open(file_path, 'rb') as file:
    #         file_data = file.read()
    # except FileNotFoundError:
    #     print(f"File not found: {{file_path}}")
    #     return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED 
        context.check_hostname = False
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        

        with context.wrap_socket(s, server_side=False, server_hostname=server_address) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {{server_address}}:{{server_port}}")
                
                # Send the file data
                send_bytes = 0
                with open(file_path, 'rb') as file:
                    while True:
                        file_data = file.read(1024)
                        if not file_data:
                            break
                        ssl_socket.sendall(file_data)
                        send_bytes += len(file_data)
                print("File sent successfully. Total bytes sent:", send_bytes)
            except Exception as e:
                print(f"Error occurred while sending file: {{e}}")
# Usage example
send_file("$temp_dir/$archive_name", "$ip_address",$port, "ca.crt")
END
}}
file_send_start_time=$(date +%s.%N)
send_file &
wait $!
echo "Dataset folder transferred successfully."
file_send_end_time=$(date +%s.%N)

rm -rf "$temp_dir/$archive_name"
wait $!
echo "Connecting to model owner for predicted labels..."
wait $!
# Function to receive files
receive_file() {{
    # Create a TCP/IP socket
    python3 - <<END
import socket
import ssl

def receive_file(peer_ip, peer_port, file_name, server_cert, server_key):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the server address and port
        s.bind((peer_ip, peer_port))
        # Listen for incoming connections
        s.listen(1)
        print(f"Waiting for connection on {{peer_ip}}:{{peer_port}}...")

        # Accept the connection
        client_socket, client_address = s.accept()
        print(f"Connected to {{client_address}}")

        # Wrap the client socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        context.load_verify_locations(cafile="ca.crt")
        context.verify_mode = ssl.CERT_NONE
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(client_socket, server_side=True) as ssl_socket:
            # Receive the file data
            with open(file_name, 'wb') as file:
                while True:
                    data = ssl_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)

            print("File received successfully.")


# Usage example
receive_file("0.0.0.0", $port, 'data.tar.gz', 'server.crt', 'server.key')
END
}}

file_receive_start_time=$(date +%s.%N)
# Start receiving the dataset folder
receive_file &
wait $!
file_receive_end_time=$(date +%s.%N)
# Clean up temporary directory
rm -rf "$temp_dir"
wait $!
#unzip the file
tar -xvf data.tar.gz
echo "predicted labels folder received successfully."
wait $!
echo "Running model accuracy tests..."
python3.10 $path_to_test > output_file.log
wait $!
echo "Model accuracy tests completed successfully."

log_file="output_file.log"
model_id={model.id}
model_name="{model.name}"
owner_name="{model.user}"
dataset_id={dataset.id}

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
    auth_token = '{Auth_token}'
    csrf_token = '{csrf_token}'
    payload = {{
        'model_id': model_id,
        'dataset_id': dataset_id,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
    }}
    cookies = {{
    'sessionid': auth_token,
    'csrftoken': csrf_token,
}}

    response = requests.post('http://{website_ip}:8000/leaderboard/update', data=payload, cookies=cookies)
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
end_time_full=$(date +%s.%N)
echo "Total time taken for the evaluation: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for dataset transfer: $(echo "$file_send_end_time - $file_send_start_time" | bc) seconds"
echo "Time taken for predicted labels transfer: $(echo "$file_receive_end_time - $file_receive_start_time" | bc) seconds"
'''

        # Script section for model evaluation
        if request.user == evaluation_request.model.user:
            script_content += f'''
            # Check if the number of arguments is correct
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <evaluation_file_path> <ip_address> <port> <folder_path>"
    exit 1
fi

# Extract arguments
evaluation_file_path=$1
ip_address=$2
port=$3
folder_path=$4

start_time_full=$(date +%s.%N)
echo "Connecting to dataset owner..."
# Function to receive files
receive_file() {{
    # Create a TCP/IP socket
    python3 - <<END
import socket
import ssl

def receive_file(peer_ip, peer_port, file_name, server_cert, server_key):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the server address and port
        s.bind((peer_ip, peer_port))
        # Listen for incoming connections
        s.listen(1)
        print(f"Waiting for connection on {{peer_ip}}:{{peer_port}}...")

        # Accept the connection
        client_socket, client_address = s.accept()
        print(f"Connected to {{client_address}}")

        # Wrap the client socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        context.load_verify_locations(cafile="ca.crt")
        context.verify_mode = ssl.CERT_NONE
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(client_socket, server_side=True) as ssl_socket:
            # Receive the file data
            with open(file_name, 'wb') as file:
                while True:
                    data = ssl_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)

            print("File received successfully.")


# Usage example
receive_file("0.0.0.0", $port, 'data.tar.gz', 'server.crt', 'server.key')
END
}}
file_receive_start_time=$(date +%s.%N)
# Start receiving the dataset folder
receive_file &
wait $!
file_receive_end_time=$(date +%s.%N)
tar -xzf data.tar.gz
wait $!
echo "Running model evaluation..."
# Add your model evaluation command here
eval_start_time=$(date +%s.%N)
$evaluation_file_path
#wait $!
eval_end_time=$(date +%s.%N)
rm -rf data.tar.gz
wait $!
# Add your command to retrieve accuracy results here
# Create a temporary directory to store the archive
temp_dir=$(mktemp -d)
archive_name="data.tar.gz"

# Create a tar archive of the folder
echo "Creating a tar archive of the folder..."
tar -czf "$temp_dir/$archive_name" -C "$folder_path" .

# Script section for dataset transfer
echo "Transferring predicted label folder..."

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
send_file(){{

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
python3 - <<END
import socket
import ssl

def send_file(file_path, server_address, server_port, ca):
    # Check if the file exists
    # try:
    #     with open(file_path, 'rb') as file:
    #         file_data = file.read()
    # except FileNotFoundError:
    #     print(f"File not found: {{file_path}}")
    #     return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(s, server_side=False, server_hostname=server_address) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {{server_address}}:{{server_port}}")

                # Send the file data
                with open(file_path, 'rb') as file:
                    while True:
                        file_data = file.read(1024)
                        if not file_data:
                            break
                        ssl_socket.sendall(file_data)
                print("File sent successfully.")
            except Exception as e:
                print(f"Error occurred while sending file: {{e}}")
# Usage example
send_file("$temp_dir/$archive_name", "$ip_address",$port, "ca.crt")
END
}}
file_send_start_time=$(date +%s.%N)
send_file &
wait $!
file_send_end_time=$(date +%s.%N)
echo "Predicted labels sent successfully."
echo "Results will be available on the leaderboard"
# Clean up temporary directory
rm -rf "$temp_dir"
end_time_full=$(date +%s.%N)

echo "Total time taken for the evaluation: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for dataset transfer: $(echo "$file_receive_end_time - $file_receive_start_time" | bc) seconds"
echo "Time taken for model evaluation: $(echo "$eval_end_time - $eval_start_time" | bc) seconds"
echo "Time taken for predicted labels transfer: $(echo "$file_send_end_time - $file_send_start_time" | bc) seconds"

'''

        # Prepare HTTP response with script content and the certifcate and key as a downloadable file
        script_file_path = os.path.join(tempfile.mkdtemp(), 'script.sh')
        with open(script_file_path, 'w') as script_file:
            script_file.write(script_content)
        zip_file_path = os.path.join(tempfile.mkdtemp(), 'script_and_cert.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(script_file_path, arcname='script.sh')
            zip_file.write(temp_ca_cert_path, 'ca.crt')
            zip_file.write(temp_server_cert_path, 'server.crt')
            zip_file.write(temp_server_key_path, 'server.key')
            if docker_file_path:
                 zip_file.write(docker_file_path, 'Dockerfile')
        
        # Prepare HTTP response with the zip file
        with open(zip_file_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="script_and_cert.zip"'
        
        # Clean up temporary files and directories
        os.remove(script_file_path)
        os.remove(zip_file_path)
        shutil.rmtree(temp_dir)
        
        return response
    elif(evaluation_request.is_approved_by_model_owner and evaluation_request.is_approved_by_dataset_owner and architecture_choosen==2):
        # Generate script content with runtime input parameters
        script_content = '''#!/bin/bash'''
        if request.user == evaluation_request.dataset.user:
            script_content += f'''
            # Check if the number of arguments is correct
    if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <evaluation_file_path> <ip_address> <port> <path_to_dataset> <path_to_test>"
    exit 1
fi

# Extract arguments
evaluation_file_path=$1
ip_address=$2
port=$3
path_to_dataset=$4
path_to_test=$5
start_time_full=$(date +%s.%N)
echo "Connecting to dataset owner..."
# Function to receive files
receive_file() {{
    # Create a TCP/IP socket
    python3 - <<END
import socket
import ssl

def receive_file(peer_ip, peer_port, file_name, server_cert, server_key):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the server address and port
        s.bind((peer_ip, peer_port))
        # Listen for incoming connections
        s.listen(1)
        print(f"Waiting for connection on {{peer_ip}}:{{peer_port}}...")

        # Accept the connection
        client_socket, client_address = s.accept()
        print(f"Connected to {{client_address}}")

        # Wrap the client socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        context.load_verify_locations(cafile="ca.crt")
        context.verify_mode = ssl.CERT_NONE
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(client_socket, server_side=True) as ssl_socket:
            # Receive the file data
            with open(file_name, 'wb') as file:
                while True:
                    data = ssl_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)

            print("File received successfully.")


# Usage example
receive_file("0.0.0.0", $port, 'model.tar.gz', 'server.crt', 'server.key')
END
}}
# Start receiving the dataset folder
file_receive_start_time=$(date +%s.%N)
receive_file &
wait $!
file_receive_end_time=$(date +%s.%N)
#unzip the file
tar -xvf model.tar.gz
echo "dataset folder received successfully."
echo "Running model evaluation..."
# Add your model evaluation command here
eval_start_time=$(date +%s.%N)
$evaluation_file_path
echo "Retrieving accuracy results..."
eval_end_time=$(date +%s.%N)
echo "Running model accuracy tests..."
python3 $path_to_test > output_file.log
wait $!
echo "Model accuracy tests completed successfully."

log_file="output_file.log"
model_id={model.id}
model_name="{model.name}"
owner_name="{model.user}"
dataset_id={dataset.id}

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
    auth_token = '{Auth_token}'
    csrf_token = '{csrf_token}'
    payload = {{
        'model_id': model_id,
        'dataset_id': dataset_id,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
    }}
    cookies = {{
    'sessionid': auth_token,
    'csrftoken': csrf_token,
}}

    response = requests.post('http://{website_ip}:8000/leaderboard/update', data=payload, cookies=cookies)
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
end_time_full=$(date +%s.%N)
echo "Total time taken for the evaluation: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for dataset transfer: $(echo "$file_receive_end_time - $file_receive_start_time" | bc) seconds"
echo "Time taken for model evaluation: $(echo "$eval_end_time - $eval_start_time" | bc) seconds"

'''
        if request.user == evaluation_request.model.user:
             script_content+=f'''
# Check if the number of arguments is correct
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <folder_path> <ip_address> <port>"
    exit 1
fi

# Extract arguments
folder_path=$1
ip_address=$2
port=$3
start_time_full=$(date +%s.%N)
# Create a temporary directory to store the archive
temp_dir=$(mktemp -d)
archive_name="data.tar.gz"

# Create a tar archive of the folder
echo "Creating a tar archive of the folder..."
tar -czf "$temp_dir/$archive_name" -C "$folder_path" .

# Script section for model transfer
echo "Transferring model folder..."
echo "Transferring model folder to dataset owner..."

send_file(){{

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
python3 - <<END
import socket
import ssl

def send_file(file_path, server_address, server_port, ca):
    # Check if the file exists
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
    except FileNotFoundError:
        print(f"File not found: {{file_path}}")
        return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(s, server_side=False, server_hostname=server_address) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {{server_address}}:{{server_port}}")

                # Send the file data
                ssl_socket.sendall(file_data)
                print("File sent successfully.")
            except Exception as e:
                print(f"Error occurred while sending file: {{e}}")
# Usage example
send_file("$temp_dir/$archive_name", "$ip_address",$port, "ca.crt")
END
}}
file_send_start_time=$(date +%s.%N)
send_file &
wait $!
file_send_end_time=$(date +%s.%N)
echo "Model transferred successfully."
echo "Model sent successfully."
echo "Results will be available on the leaderboard"

echo "Total time taken: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for model transfer: $(echo "$file_send_end_time - $file_send_start_time" | bc) seconds"

'''
        script_file_path = os.path.join(tempfile.mkdtemp(), 'script.sh')
        with open(script_file_path, 'w') as script_file:
            script_file.write(script_content)
        zip_file_path = os.path.join(tempfile.mkdtemp(), 'script_and_cert.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(script_file_path, arcname='script.sh')
            zip_file.write(temp_ca_cert_path, 'ca.crt')
            zip_file.write(temp_server_cert_path, 'server.crt')
            zip_file.write(temp_server_key_path, 'server.key')
            if docker_file_path:
                 zip_file.write(docker_file_path, 'Dockerfile')
        
        # Prepare HTTP response with the zip file
        with open(zip_file_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="script_and_cert.zip"'
        
        # Clean up temporary files and directories
        os.remove(script_file_path)
        os.remove(zip_file_path)
        shutil.rmtree(temp_dir)

        return response
    elif(evaluation_request.is_approved_by_model_owner and evaluation_request.is_approved_by_dataset_owner and architecture_choosen==3):
        third_party = TrustedThirdParty.objects.filter(id=1)
        # Generate script content with runtime input parameters
        script_content = '''#!/bin/bash'''
        if request.user == evaluation_request.dataset.user:
            script_content += f'''
            # Check if the number of arguments is correct
            Third_party_ip_address={third_party.ip_address}
            Third_party_port=7002
            verification_code=1234
            dataset_file_path=$1

            if [ "$#" -ne 2 ]; then
                echo "Usage: $0 <dataset_file_path> <verification code>"
                exit 1
            fi
            ip_address=$Third_party_ip_address
port=$Third_party_port
start_time_full=$(date +%s.%N) 
# Create a temporary directory to store the archive
temp_dir=$(mktemp -d)
wait $!
archive_name="dataset.tar.gz"

# Create a tar archive of the folder
echo "Creating a tar archive of the folder..."
tar -czf "$temp_dir/$archive_name" -C "$dataset_file_path" .
wait $!
# Script section for dataset transfer
echo "Transferring dataset folder..."
echo "Transferring dataset folder to model owner..."
send_file(){{

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
python3 - <<END
import socket
import ssl

def send_file(file_path, server_address, server_port, ca):
    # Check if the file exists
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
    except FileNotFoundError:
        print(f"File not found: {{file_path}}")
        return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(s, server_side=False, server_hostname=server_address) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {{server_address}}:{{server_port}}")

                # Send the file data
                ssl_socket.sendall(file_data)
                print("File sent successfully.")
            except Exception as e:
                print(f"Error occurred while sending file: {{e}}")
# Usage example
send_file("$temp_dir/$archive_name", "$ip_address",$port, "ca.crt")
END
}}
file_send_start_time=$(date +%s.%N)
send_file &
wait $!
file_send_end_time=$(date +%s.%N)
echo "Dataset folder transferred successfully."
echo "Results will be available on the leaderboard"
echo "Total time taken: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for dataset transfer: $(echo "$file_send_end_time - $file_send_start_time" | bc) seconds"
            '''
        if request.user == evaluation_request.model.user:
             script_content += f'''
                # Check if the number of arguments is correct
            Third_party_ip_address={third_party.ip_address}
            Third_party_port=7001
            verification_code=1234
            model_file_path=$1

            if [ "$#" -ne 2 ]; then
                echo "Usage: $0 <model_file_path> <verification code>"
                exit 1
            fi
            ip_address=$Third_party_ip_address
port=$Third_party_port
            
start_time_full=$(date +%s.%N)
# Create a temporary directory to store the archive
temp_dir=$(mktemp -d)
wait $!
archive_name="model.tar.gz"

# Create a tar archive of the folder
echo "Creating a tar archive of the folder..."
tar -czf "$temp_dir/$archive_name" -C "$model_file_path" .
wait $!
# Script section for model transfer
echo "Transferring model folder..."
echo "Transferring model folder to model owner..."
send_file(){{

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
python3 - <<END
import socket
import ssl

def send_file(file_path, server_address, server_port, ca):
    # Check if the file exists
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
    except FileNotFoundError:
        print(f"File not found: {{file_path}}")
        return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(s, server_side=False, server_hostname=server_address) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {{server_address}}:{{server_port}}")

                # Send the file data
                ssl_socket.sendall(file_data)
                print("File sent successfully.")
            except Exception as e:
                print(f"Error occurred while sending file: {{e}}")
# Usage example
send_file("$temp_dir/$archive_name", "$ip_address",$port, "ca.crt")
END
}}
file_send_start_time=$(date +%s.%N)
send_file &
wait $!
file_send_end_time=$(date +%s.%N)
echo "model folder transferred successfully."
echo "Results will be available on the leaderboard"
echo "Total time taken: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for model transfer: $(echo "$file_send_end_time - $file_send_start_time" | bc) seconds"
            '''
             code=third_party.auth_token
             send_metadata_to_third_party(model, dataset, evaluation_request, third_party.ip_address, third_party.port, code,temp_ca_cert_path, temp_server_cert_path, temp_server_key_path)
        script_file_path = os.path.join(tempfile.mkdtemp(), 'script.sh')
        with open(script_file_path, 'w') as script_file:
            script_file.write(script_content)
        zip_file_path = os.path.join(tempfile.mkdtemp(), 'script_and_cert.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(script_file_path, arcname='script.sh')
            zip_file.write(temp_ca_cert_path, 'ca.crt')
            zip_file.write(temp_server_cert_path, 'server.crt')
            zip_file.write(temp_server_key_path, 'server.key')

        # Prepare HTTP response with the zip file
        with open(zip_file_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="script_and_cert.zip'

        # Clean up temporary files and directories
        os.remove(script_file_path)
        os.remove(zip_file_path)
        shutil.rmtree(temp_dir)
        

        return response
    elif(evaluation_request.is_approved_by_model_owner and evaluation_request.is_approved_by_dataset_owner and architecture_choosen==4):
        cc=confidential_compute.objects.get(id=1)
         # Generate script content with runtime input parameters
        script_content = '''#!/bin/bash'''
        if request.user == evaluation_request.dataset.user:
            script_content += f'''
            # Check if the number of arguments is correct
            cc_ip_address={cc.ip_address}
            cc_port=7002
            verification_code=1234
            dataset_file_path=$1

            if [ "$#" -ne 2 ]; then
                echo "Usage: $0 <dataset_file_path> <verification code>"
                exit 1
            fi
            ip_address=$cc_ip_address
port=$cc_port

start_time_full=$(date +%s.%N)  
# Create a temporary directory to store the archive
temp_dir=$(mktemp -d)
wait $!
archive_name="dataset.tar.gz"

# Create a tar archive of the folder
echo "Creating a tar archive of the folder..."
tar -czf "$temp_dir/$archive_name" -C "$dataset_file_path" .
wait $!
# Script section for dataset transfer
echo "Transferring dataset folder..."
echo "Transferring dataset folder to model owner..."
send_file(){{

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
python3 - <<END
import socket
import ssl

def send_file(file_path, server_address, server_port, ca):
    # Check if the file exists
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
    except FileNotFoundError:
        print(f"File not found: {{file_path}}")
        return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(s, server_side=False, server_hostname=server_address) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {{server_address}}:{{server_port}}")

                # Send the file data
                ssl_socket.sendall(file_data)
                print("File sent successfully.")
            except Exception as e:
                print(f"Error occurred while sending file: {{e}}")
# Usage example
send_file("$temp_dir/$archive_name", "$ip_address",$port, "ca.crt")
END
}}
file_send_start_time=$(date +%s.%N)
send_file &
wait $!
file_send_end_time=$(date +%s.%N)
echo "Dataset folder transferred successfully."
echo "Results will be available on the leaderboard"
echo "Total time taken: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for dataset transfer: $(echo "$file_send_end_time - $file_send_start_time" | bc) seconds"
            '''
        if request.user == evaluation_request.model.user:
             script_content += f'''
                # Check if the number of arguments is correct
            cc_ip_address={cc.ip_address}
            cc_port=7001
            verification_code=1234
            model_file_path=$1

            if [ "$#" -ne 2 ]; then
                echo "Usage: $0 <model_file_path> <verification code>"
                exit 1
            fi
            ip_address=$cc_ip_address
port=$cc_port
            
start_time_full=$(date +%s.%N)
# Create a temporary directory to store the archive
temp_dir=$(mktemp -d)
wait $!
archive_name="model.tar.gz"

# Create a tar archive of the folder
echo "Creating a tar archive of the folder..."
tar -czf "$temp_dir/$archive_name" -C "$model_file_path" .
wait $!
# Script section for model transfer
echo "Transferring model folder..."
echo "Transferring model folder to model owner..."
send_file(){{

# Use openssl to transfer the tar archive over TLSv1.3 and specify the certificate and key
python3 - <<END
import socket
import ssl

def send_file(file_path, server_address, server_port, ca):
    # Check if the file exists
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
    except FileNotFoundError:
        print(f"File not found: {{file_path}}")
        return

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=ca)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2


        with context.wrap_socket(s, server_side=False, server_hostname=server_address) as ssl_socket:
            try:
                # Connect to the server
                ssl_socket.connect((server_address, server_port))
                print(f"Connected to {{server_address}}:{{server_port}}")

                # Send the file data
                ssl_socket.sendall(file_data)
                print("File sent successfully.")
            except Exception as e:
                print(f"Error occurred while sending file: {{e}}")
# Usage example
send_file("$temp_dir/$archive_name", "$ip_address",$port, "ca.crt")
END
}}
file_send_start_time=$(date +%s.%N)
send_file &
wait $!
file_send_end_time=$(date +%s.%N)
echo "model folder transferred successfully."
echo "Results will be available on the leaderboard"
echo "Total time taken: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for model transfer: $(echo "$file_send_end_time - $file_send_start_time" | bc) seconds"
            '''
             code=cc.auth_token
             send_metadata_to_cc(model, dataset, evaluation_request, cc.ip_address, cc.port, code,temp_ca_cert_path, temp_server_cert_path, temp_server_key_path)
        script_file_path = os.path.join(tempfile.mkdtemp(), 'script.sh')
        with open(script_file_path, 'w') as script_file:
            script_file.write(script_content)
        zip_file_path = os.path.join(tempfile.mkdtemp(), 'script_and_cert.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(script_file_path, arcname='script.sh')
            zip_file.write(temp_ca_cert_path, 'ca.crt')
            zip_file.write(temp_server_cert_path, 'server.crt')
            zip_file.write(temp_server_key_path, 'server.key')

        # Prepare HTTP response with the zip file
        with open(zip_file_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="script_and_cert.zip'

        # Clean up temporary files and directories
        os.remove(script_file_path)
        os.remove(zip_file_path)
        shutil.rmtree(temp_dir)
        

        return response
    elif(evaluation_request.is_approved_by_model_owner and evaluation_request.is_approved_by_dataset_owner and architecture_choosen==5):
         # Generate script content with runtime input parameters
        script_content = '''#!/bin/bash'''
        
        if request.user == evaluation_request.dataset.user:
            script_content += f'''
            # Check if the number of arguments is correct
            if [ "$#" -ne 5 ]; then
                echo "Usage: $0 <dataset_path> <key_path> <batch_size> <number of Embeddings> <verification_code>"
                exit 1
            fi
            dataset_path=$1
            key_path=$2
            batch_size=$3
            number_of_embeddings=$4
            verification_code=$5
            start_time_full=$(date +%s.%N)
            # Run the metadata script on the dataset
            metadata_start_time=$(date +%s.%N)
            echo "Running metadata script on the dataset..."
	        ./generate_metadata.sh --batch_size $batch_size --n_embd $number_of_embeddings --path $dataset_path
            wait $!
            echo "Metadata script completed successfully."
            metadata_end_time=$(date +%s.%N)
            # send the metadata to the platform
            echo "Sending metadata to the platform..."
            # Function to send metadata.txt file
            send_metadata() {{
                python3 - <<END
import requests
import json

def send_metadata(metadata_file, verification_code):
    # URL to send metadata to
    url = 'http://{website_ip}:8000/evaluation/ezpc_metadata'
    # Verification code
    verification_code = verification_code
    # Metadata file
    files = {{
        'metadata_file': open(metadata_file, 'rb')
    }}
    # Data to send
    data = {{
        'verification_code': verification_code,
        'request_id': '42'
    }}
    # Send metadata
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print("Metadata sent successfully.")
    else:
        print("Error sending metadata:", response.text)

# Usage example
send_metadata('metadata.txt', '$verification_code')
END
            }}
            send_metadata_start_time=$(date +%s.%N)
            send_metadata &
            send_metadata_end_time=$(date +%s.%N)
            echo "Waiting to receive the key files from the website..."
            # Function to receive key files

            receive_key_files() {{
                python3 - <<END
import socket
import ssl
from tqdm import tqdm
import os

def receive_key_files(peer_ip, peer_port, file_name, server_cert, server_key):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the server address and port
        s.bind((peer_ip, peer_port))
        # Listen for incoming connections
        s.listen(1)
        print(f"Waiting for connection on {{peer_ip}}:{{peer_port}}...")
        # Accept the connection
        client_socket, client_address = s.accept()
        print(f"Connected to {{client_address}}")
        # Wrap the client socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        context.load_verify_locations(cafile="./ca.crt")
        context.verify_mode = ssl.CERT_NONE
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        with context.wrap_socket(client_socket, server_side=True) as ssl_socket:
            # Receive the folder path
            folder_path = ssl_socket.recv(1024).decode()
            print(f"Receiving folder from {{folder_path}}")

            # Receive the number of files
            num_files = int(ssl_socket.recv(1024).decode())
            print(f"Receiving {{num_files}} files")
            save_directory=file_name
            # Create save directory if it doesn't exist
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # Receive the files
            for _ in range(num_files):
                # Receive the file name
                file_name = ssl_socket.recv(1024).decode()
                if not file_name:
                    break
                print(f"Receiving file: {{file_name}}")

                # Receive the file size
                file_size = int(ssl_socket.recv(1024).decode())

                # Open a file for writing
                file_path = os.path.join(save_directory, file_name)
                with open(file_path, "wb") as f:
                    # Receive and write file data
                    received_bytes = 0
                    while received_bytes < file_size:
                        remaining_bytes = file_size - received_bytes
                        chunk_size = min(1024, remaining_bytes)
                        file_data = ssl_socket.recv(chunk_size)
                        if not file_data:
                            break
                        f.write(file_data)
                        received_bytes += len(file_data)

                # Confirm receipt of the file
                ssl_socket.sendall(b"Received")
                print(f"Received {{file_name}}")

            print("Folder received successfully")
                

# Usage example
receive_key_files({website_ip}, 9000, 'key_files_dataset', './server.crt', './server.key')
END
            }}
            receive_key_files_start_time=$(date +%s.%N)
            receive_key_files

            wait $!
            echo "Key files received successfully."
            receive_key_files_end_time=$(date +%s.%N)
            # Starting evaluation using EzPC
            evaluation_start_time=$(date +%s.%N)
            Ezpc_path="./executables/bertezpc"
            if [ ! -f "$Ezpc_path" ]; then
                echo "EzPC executable not found. Please build the EzPC project first."
                exit 1
            fi
            echo "Starting evaluation using EzPC..."
            #iterate over the dataset path and run the evaluation script on each input .dat file where id variable keeps track of the number of files
            id=0
            
            touch predicted_output.txt
            for file in inputs/*.dat;
            do
               complete_path=$(realpath $file)
               echo $complete_path
               $Ezpc_path 3 ip={evaluation_request.ip_address} in_file=$complete_path key_path=$key_path id=$id nt=8 > output_dataset/$id.log
               wait $!
               #currently set for bert model and sst2 dataset !!!!!!!!!!!!!!! change here !!!!!!!!!!!!!!!!!!!!
               #get the last two lines of output to check if the evaluation was successful
               res0= tail -n 1 output_dataset/$id.log
               #get the second last line of output
               res1= tail -n 2 output_dataset/$id.log | head -n 1
               #compare the last two lines 
               if [ $res0 > $res1 ]; then
                   echo "0" >>predicted_output.txt
               else
                   echo "1" >>predicted_output.txt
               fi


               if(( $?)); then
                   echo "Error in running the evaluation script."
                   exit 1
               fi
               id=$((id+1))
            done
            evaluation_end_time=$(date +%s.%N)
            #upload results to the platform
            echo "Uploading results to the platform..."
            # generate the results 
            python3 ./generate_results.py --ground_truth_labels_file ./dataset/sst2/labels.txt --predicted_labels_file ./predicted_output.txt > results.txt
            # Function to send results
    
            wait $!

log_file="results.txt"
model_id={model.id}
model_name="{model.name}"
owner_name="{model.user}"
dataset_id={dataset.id}

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
    auth_token = '{Auth_token}'
    csrf_token = '{csrf_token}'
    payload = {{
        'model_id': model_id,
        'dataset_id': dataset_id,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
    }}
    cookies = {{
    'sessionid': auth_token,
    'csrftoken': csrf_token,
}}

    response = requests.post('http://{website_ip}:8000/leaderboard/update', data=payload, cookies=cookies)
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
end_time_full=$(date +%s.%N)
echo "Total time taken for the evaluation: $(echo "$end_time_full - $start_time_full" | bc) seconds"
echo "Time taken for metadata generation: $(echo "$metadata_end_time - $metadata_start_time" | bc) seconds"
echo "Time taken for key transfer: $(echo "$receive_key_files_end_time - $receive_key_files_start_time" | bc) seconds"
echo "Time taken for model evaluation: $(echo "$evaluation_end_time - $evaluation_start_time" | bc) seconds"
echo "Time taken for sending metadata: $(echo "$send_metadata_end_time - $send_metadata_start_time" | bc) seconds"

            '''
        if request.user == evaluation_request.model.user:
             script_content += f'''
            # Check if the number of arguments is correct
            if [ "$#" -ne 3 ]; then
                echo "Usage: $0 <model_weights> <key_path> <verification_code>"
                exit 1

            fi
            model_weights=$1
            key_path=$2
            verification_code=$3
            start_time_full=$(date +%s.%N)
            key_received_start_time=$(date +%s.%N)
            # weight for keys from the platform
            echo "waiting for the keys from the platform..."
            # Function to receive keys
            receive_keys() {{
                python3 - <<END
import socket
import ssl
from tqdm import tqdm
import os
import json

def receive_key_files(peer_ip, peer_port, file_name, server_cert, server_key):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the server address and port
        s.bind((peer_ip, peer_port))
        # Listen for incoming connections
        s.listen(1)
        print(f"Waiting for connection on {{peer_ip}}:{{peer_port}}...")
        # Accept the connection
        client_socket, client_address = s.accept()
        print(f"Connected to {{client_address}}")
        # Wrap the client socket in TLS encryption
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        context.load_verify_locations(cafile="./ca.crt")
        context.verify_mode = ssl.CERT_NONE
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        with context.wrap_socket(client_socket, server_side=True) as ssl_socket:
            # Receive the folder path
            folder_path = ssl_socket.recv(1024).decode()
            print(f"Receiving folder from {{folder_path}}")

            # Receive the number of files
            num_files = int(ssl_socket.recv(1024).decode())
            print(f"Receiving {{num_files}} files")
            save_directory=file_name
            # Create save directory if it doesn't exist
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # Receive the files
            for _ in range(num_files):
                # Receive the file name
                file_name = ssl_socket.recv(1024).decode()
                if not file_name:
                    break
                print(f"Receiving file: {{file_name}}")

                # Receive the file size
                file_size = int(ssl_socket.recv(1024).decode())

                # Open a file for writing
                file_path = os.path.join(save_directory, file_name)
                with open(file_path, "wb") as f:
                    # Receive and write file data
                    received_bytes = 0
                    while received_bytes < file_size:
                        remaining_bytes = file_size - received_bytes
                        chunk_size = min(1024, remaining_bytes)
                        file_data = ssl_socket.recv(chunk_size)
                        if not file_data:
                            break
                        f.write(file_data)
                        received_bytes += len(file_data)

                # Confirm receipt of the file
                ssl_socket.sendall(b"Received")
                print(f"Received {{file_name}}")

            print("Folder received successfully")
                

receive_key_files('{website_ip}', 9001, 'key_files_model', './server.crt', './server.key')
END
            }}
            receive_keys

            wait $!
            key_received_end_time=$(date +%s.%N)
            echo "Keys received successfully."
            # Run the evaluation script
            Ezpc_path="./executables/bertezpc"
            if [ ! -f "$Ezpc_path" ]; then
                echo "EzPC executable not found. Please build the EzPC project first."
                exit 1
            fi
            echo "Running the evaluation script..."
            #iterate over the received key files
            eval_start_time=$(date +%s.%N)
            id=0 
            for file in key_files_model/*.dat
            do
                $Ezpc_path 2 wt_file=$model_weights key_path=$key_path id=$id nt=8 > output_model/$id.log
                id=$((id+1))
            done
            eval_end_time=$(date +%s.%N)
            end_time_full=$(date +%s.%N)
            echo "Evaluation completed successfully."
            echo "Results will be available on the leaderboard"
            echo "Total time taken: $(echo "$end_time_full - $start_time_full" | bc) seconds"
            echo "Time taken for key transfer: $(echo "$key_received_end_time - $key_received_start_time" | bc) seconds"
            echo "Time taken for model evaluation: $(echo "$eval_end_time - $eval_start_time" | bc) seconds"
            
            '''
        script_file_path = os.path.join(tempfile.mkdtemp(), 'script.sh')
        with open(script_file_path, 'w') as script_file:
            script_file.write(script_content)
        zip_file_path = os.path.join(tempfile.mkdtemp(), 'script_and_cert.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(script_file_path, arcname='script.sh')
            zip_file.write(temp_ca_cert_path, 'ca.crt')
            zip_file.write(temp_server_cert_path, 'server.crt')
            zip_file.write(temp_server_key_path, 'server.key')
            if(docker_file_path):
                zip_file.write(docker_file_path, 'Dockerfile')
            if(request.user == evaluation_request.dataset.user):
                zip_file.write(metadata_file_path, 'generate_metadata.sh')
                zip_file.write(generate_results_file_path, 'generate_results.py')
        
        # Prepare HTTP response with the zip file
        with open(zip_file_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="script_and_cert.zip'
        
        # Clean up temporary files and directories
        os.remove(script_file_path)
        os.remove(zip_file_path)
        shutil.rmtree(temp_dir)

        return response

    else:
        # Handle case where request is not approved by both owners
        return HttpResponse("Request not approved by both owners.")



@login_required
def evaluate_request_response(request, request_id):
    print("Inside evaluate_request_response view")  # Debugging output
    print(request.user)  # Debugging output
    print(request.POST)  # Debugging output
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        action = data.get('action')
        print(action)
        evaluation_request = get_object_or_404(Evaluation, pk=request_id)

        if action == 'approve':
            
            if request.user == evaluation_request.model.user:
                # Model owner approves the request
                evaluation_request.is_approved_by_model_owner = True
                evaluation_request.status = 'Approved by model owner'
                evaluation_request.save()

            if request.user == evaluation_request.dataset.user:
                # Dataset owner approves the request
                evaluation_request.is_approved_by_dataset_owner = True
                evaluation_request.status = 'Approved by dataset owner'
                evaluation_request.save()

            # Check if both model owner and dataset owner have approved
            if evaluation_request.is_approved_by_model_owner and evaluation_request.is_approved_by_dataset_owner:
                evaluation_request.status = 'Approved'
                evaluation_request.save()
                return JsonResponse({'message':' Evaluation request approved successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Evaluation request approved by one owner. Waiting for another owner.'}, status=200)


        elif action == 'decline':
            # Handle decline logic
            evaluation_request.status = 'Declined'
            evaluation_request.save()
            return JsonResponse({'message': 'Evaluation request declined successfully.'}, status=200)


        else:
            return JsonResponse({'error': 'Invalid action.'}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

def leaderboard(request):
    # Fetch leaderboard entries and sort by accuracy (descending order)
    leaderboard_entries = LeaderboardEntry.objects.order_by('-accuracy')
    modelall=ModelArchitecture.objects.all()
    # Render the leaderboard template with leaderboard entries with rank

    return render(request, 'main/leaderboard.html', {'leaderboard_entries': leaderboard_entries,'all_models':modelall})

def platform_ezpc_processing(metadata_file_path,evaluation_request,dataset_ip_received,dataset_port_received):
     model_id=evaluation_request.model.id
     dataset_id=evaluation_request.dataset.id
     os.chdir(settings.BASE_DIR)
     os.chdir("../gpt-ezpc/sytorch/LLMs/configs")
     os.system(f"cp config{model_id}.json ../config.json")
     os.chdir("../")
     model_ip_received=evaluation_request.ip_address
     model_port_received=9001
     print(model_ip_received)
     print(model_port_received)
     print(dataset_ip_received)
     print(dataset_port_received)
     # iterate over metadatafile and run the evaluation script on each input .dat file where id variable keeps track of the number of files
     id=0
     
     with open(metadata_file_path, 'r') as f:
          for line in f:
            #split the line to get the file name
            filename=line.split()
            #run the evaluation script on the file
            print(filename)
            os.system(f"./executables/bertezpc 1 n_seq={filename[0]} key_path=./ezpc_keys/ id={id} nt=8")
            #wait for the command to complete
            id=id+1

        #send the generated keys to the client and server simultaneously
     subprocess.run(['python3', 'send_keys.py', 'dataset', str(id), str(dataset_ip_received), str(dataset_port_received)],check=True)
     subprocess.run(['python3', 'send_keys.py', 'model', str(id), str(model_ip_received), str(model_port_received)],check=True)


@require_POST
@csrf_exempt
def ezpc_metadata(request):
     #receive a metadata.txt file from the dataset owner and also check the verification code to ensure that the metadata is coming from the dataset owner
     if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        request_id = request.POST.get('request_id')
        evaluation_request = get_object_or_404(Evaluation, pk=request_id)
        evaluationid=evaluation_request.id
        if verification_code == '1234':
            metadata_file = request.FILES.get('metadata_file')
            metadata_file = uuid.uuid4().hex
            metadata_file_path = os.path.join(settings.MEDIA_ROOT, 'metadata','evaluationid'+str(evaluationid)+'_'+metadata_file.name)
            with open(metadata_file_path, 'wb') as file:
                for chunk in metadata_file.chunks():
                    file.write(chunk)
            # Save the metadata file to the database
            ezpc_metadata_id = EzPCMetadata.objects.create(evaluation=evaluation_request, metadata=metadata_file_path)
            dataset_ip_received=request.META.get('REMOTE_ADDR')
            dataset_port_received='9000'
            platform_ezpc_processing(metadata_file_path,evaluation_request,dataset_ip_received,dataset_port_received)
            return JsonResponse({'message': 'Metadata received successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid verification code'}, status=400)
          

@require_POST
@csrf_exempt
def update_leaderboard(request):
    # Ensure that the authenticated user is the model owner user
    model_id = request.POST.get('model_id')
    dataset_id = request.POST.get('dataset_id')
    print(model_id)
    print(dataset_id)
    model = get_object_or_404(ModelArchitecture, pk=model_id)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    ttp_user_token = TrustedThirdParty.objects.get(id=1).auth_token
    if (request.user == dataset.user) or (request.COOKIES.get('auth_token') == ttp_user_token):
        accuracy = request.POST.get('accuracy')
        if accuracy:
            # Create or update the leaderboard entry
            LeaderboardEntry.objects.update_or_create(
                model_owner=model.user,
                model_name=model,
                dataset=dataset,
                accuracy=accuracy,
                precision=request.POST.get('precision'),
                recall=request.POST.get('recall'),
                f1_score=request.POST.get('f1_score'),
            )
            return JsonResponse({'message': 'Leaderboard updated successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Accuracy not provided'}, status=400)
    else:
        return JsonResponse({'error': 'Unauthorized'}, status=403)