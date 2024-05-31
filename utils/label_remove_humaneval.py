import os

def load_humaneval_dataset():
    from datasets import load_dataset
    dataset = load_dataset('dataset_files/openai_humaneval')
    return dataset

def remove_labels(dataset):
    dataset = dataset.remove_columns('canonical_solution')
    return dataset

def get_test_split(dataset):
    test_dataset = dataset['test']
    return test_dataset

def save_test_split(test_dataset):
    test_dataset.save_to_disk('./humaneval_test/')
    print('Test split saved to disk')

load_humaneval_dataset = load_humaneval_dataset()
dataset = remove_labels(load_humaneval_dataset)
test_dataset = get_test_split(dataset)
save_test_split(test_dataset)