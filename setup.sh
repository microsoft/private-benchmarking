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
cd GPU-MPC
chmod +x setup.sh
export CUDA_VERSION=11.8 #change this according to your system config
export CUDA_ARCH=90 #change this according to your system config
./setup.sh
make sigma_offline_online