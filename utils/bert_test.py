from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datasets import load_dataset

# Load SST-2 dataset
dataset = load_dataset("glue", "sst2")

# Load predicted labels from file
predicted_labels = []
with open("predicted_labels.txt", "r") as f:
    for line in f:
        predicted_labels.append(int(line.strip()))

# Get true labels from the dataset
true_labels = dataset["test"]["label"]

# Map labels to binary values (0 and 1)
true_labels = [1 if label == 1 else 0 for label in true_labels]

# Compute metrics
accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels)

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
