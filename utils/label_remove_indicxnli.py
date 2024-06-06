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