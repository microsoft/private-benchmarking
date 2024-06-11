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
import argparse
from datasets import load_dataset
import os


def download_dataset(dataset_name):
    if dataset_name == 'Divyanshu/indicxnli':
        dataset = load_dataset(dataset_name,"hi")
        dataset = dataset.map(lambda x: {"premise": x["premise"].strip()})
        dataset = dataset.map(lambda x: {"hypothesis": x["hypothesis"].strip()})
    else:
        dataset = load_dataset(dataset_name)
    dataset_dir = './dataset_files/{}/'.format(dataset_name)
    os.makedirs(dataset_dir, exist_ok=True)
    dataset.save_to_disk(dataset_dir)
    print('Dataset saved:', dataset_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_name', nargs='?', help='Name of the datasets to download. Choose from: openai_humaneval,\n stanfordnlp/sst2,\n Divyanshu/indicxnli,\n cimec/lambada,\
                        \n cifar10')
    parser.add_argument('--all', action='store_true', help='Download all available datasets')
    args = parser.parse_args()

    if args.all:
        datasets=['openai_humaneval',
                  'stanfordnlp/sst2',
                  'Divyanshu/indicxnli',
                  'cimec/lambada',
                  'cifar10',]
    elif args.dataset_name is None:
        parser.print_help()
        exit()
    else:
        datasets = args.dataset_name.split(',')
    for dataset_name in datasets:
        download_dataset(dataset_name.strip())


#usage
# python datasets_download.py openai_humaneval
