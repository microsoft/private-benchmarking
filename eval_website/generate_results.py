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

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import argparse
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def main(args):
    # Load ground truth labels
    with open(args.ground_truth_labels_file, "r") as f:
        ground_truth_labels = [line.strip() for line in f.readlines()]

    # Load predicted labels
    with open(args.predicted_labels_file, "r") as f:
        predicted_labels = [line.strip() for line in f.readlines()]

    # Calculate metrics
    accuracy = accuracy_score(ground_truth_labels, predicted_labels)
    precision = precision_score(ground_truth_labels, predicted_labels, average="macro")
    recall = recall_score(ground_truth_labels, predicted_labels, average="macro")
    f1 = f1_score(ground_truth_labels, predicted_labels, average="macro")

    # Print metrics
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground_truth_labels_file", type=str, help="Path to the file containing ground truth labels.",default="output.txt")
    parser.add_argument("--predicted_labels_file", type=str, help="Path to the file containing predicted labels.",default="./predicted_labels.txt")
    args = parser.parse_args()
    main(args)


