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

git clone https://github.com/mpc-msri/EzPC
cd EzPC/GPU-MPC
chmod +x setup.sh
export CUDA_VERSION=11.8
export CUDA_ARCH=90
./setup.sh
make sigma_offline_online

#testing bert
echo "Testing bert"
cd experiments/sigma
./sigma_offline_online bert-base 100 0 0 ./
./sigma_offline_online bert-base 100 0 1 ./
./sigma_offline_online bert-base 100 1 0 ./ 127.0.0.1 8 &
./sigma_offline_online bert-base 100 1 1 ./ 127.0.0.1 8

#testing Airavata
echo "Testing Airavata"
./sigma_offline_online airavata 100 0 0 ./
./sigma_offline_online airavata 100 0 1 ./
./sigma_offline_online airavata 100 1 0 ./ 127.0.0.1 8 &
./sigma_offline_online airavata 100 1 1 ./ 127.0.0.1 8

#testing llama2-7B
echo "Testing llama2-7B"
./sigma_offline_online llama-7b 100 0 0 ./
./sigma_offline_online llama-7b 100 0 1 ./
./sigma_offline_online llama-7b 100 1 0 ./ 127.0.0.1 8 &
./sigma_offline_online llama-7b 100 1 1 ./ 127.0.0.1 8

cd ../..
#testing vgg16
make orca
echo "Testing vgg16"
#change the config.json according to your system config then press enter
while true; do
    read -p "Do you want to change the config.json file? (y/n)" yn
    case $yn in
        [Yy]* ) nano experiments/orca/config.json; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done
cd experiments/orca
python run_experiment.py --table 9 --party 0 &
python run_experiment.py --table 9 --party 1

