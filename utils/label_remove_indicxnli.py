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
import os

def load_indicxnli_dataset():
    from datasets import load_dataset
    dataset = load_dataset("Divyanshu/indicxnli","hi",split='test',)
    return dataset

def remove_labels(dataset):
    dataset = dataset.remove_columns('label')
    print(dataset)
    return dataset

def get_test_split(dataset):
    test_dataset = dataset['test']
    return test_dataset

def save_test_split(test_dataset):
    test_dataset.save_to_disk('./indicxnli_test/')
    print('Test split saved to disk')

# load_indicxnli_dataset = load_indicxnli_dataset()
# test_dataset = get_test_split(load_indicxnli_dataset)
 #dataset = remove_labels(test_dataset)
# save_test_split(test_dataset)
dataset=remove_labels(load_indicxnli_dataset())
save_test_split(dataset)