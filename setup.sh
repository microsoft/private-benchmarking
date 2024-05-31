#!/bin/bash

echo "Enter the IP address of the website"
read website_ip
sed -i "s/ALLOWED_HOSTS = \[\(.*\)\]/ALLOWED_HOSTS = ['localhost', '$website_ip',\1]/" eval_website/eval_website/settings.py
# Clone the submodules
git submodule update --init --recursive
sudo apt install python3-pip
# Install the required packages
pip install -r ./eval_website/requirements.txt
touch ./eval_website/.env
#setup the Environment for EzPC
cd gpt-ezpc
sudo apt update
sudo apt install libeigen3-dev cmake build-essential git sqlite3
pip install -r OnnxBridge/requirements.txt
chmod +x ./setup_env_and_build.sh
sudo ./setup_env_and_build.sh quick