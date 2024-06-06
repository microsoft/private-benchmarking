#!/bin/bash

echo "Enter the huggingface Access Token for Llama2-7B"
read llama2_7B_token
#testing bert
echo "Testing bert"
time python3 bert.py

#testing Airavata
echo "Testing Airavata"
git clone https://github.com/trajore/IndicInstruct
cd IndicInstruct
export PYTHONPATH=$PYTHONPATH:$(pwd)
git checkout dev
pip install -r requirements.txt
./scripts/prepare_eval_data.sh
time ./scripts/indic_eval/inidcxnli.sh

#testing llama2-7B
echo "Testing llama2-7B"
time python3 lambada.py $llama2_7B_token

#testing vgg16
echo "Testing vgg16"
time python3 vgg16_eval.py