#load the sst2 dataset

import os

def load_sst2_dataset():
    from datasets import load_dataset
    dataset = load_dataset('standfordnlp/sst2',split='test')
    return dataset


#remove the labels from the dataset
def remove_labels(dataset):
    dataset = dataset.remove_columns('label')
    return dataset

#get the test split of the dataset
def get_test_split(dataset):
    test_dataset = dataset['test']
    return test_dataset

#save the test split to a file
def save_test_split(test_dataset):
    test_dataset.save_to_disk('./sst2_test/')
    print('Test split saved to disk')

load_sst2_dataset = load_sst2_dataset()
dataset = remove_labels(load_sst2_dataset)
save_test_split(dataset)

