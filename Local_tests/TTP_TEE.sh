#!/bin/bash
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

echo "Enter the huggingface Access Token for Llama2-7B"
read llama2_7B_token_inp
export llama2_7B_token=$llama2_7B_token_inp
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
time ./scripts/indic_eval/indicxnli.sh

#testing llama2-7B
echo "Testing llama2-7B"
time python3 lambada.py $llama2_7B_token

#testing vgg16
echo "Testing vgg16"
time python3 vgg16_eval.py