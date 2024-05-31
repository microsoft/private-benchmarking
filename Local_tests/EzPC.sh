#!/bin/bash

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

