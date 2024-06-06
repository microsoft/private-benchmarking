#!/usr/bin/env python
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from datasets import load_dataset

# Load SST-2 dataset
dataset = load_dataset("glue", "sst2")

# Load pre-trained BERT model and tokenizer
model_name = "bert-base-cased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Tokenize and preprocess dataset
def preprocess_function(examples):
    return tokenizer(examples["sentence"], padding="max_length", truncation=True)

test_dataset = dataset["test"]
test_dataset = test_dataset.map(preprocess_function, batched=True)

# Set up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Move model to the appropriate device
model.to(device)

# Set the model to evaluation mode
model.eval()

# Define collate function to convert lists to tensors
def collate_fn(batch):
    input_ids = torch.tensor([example["input_ids"] for example in batch])
    attention_mask = torch.tensor([example["attention_mask"] for example in batch])
    return {"input_ids": input_ids, "attention_mask": attention_mask}

# Generate predictions
predicted_labels = []
data_loader = torch.utils.data.DataLoader(test_dataset, batch_size=8, collate_fn=collate_fn)
with torch.no_grad():
    for batch in data_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        outputs = model(input_ids, attention_mask=attention_mask)
        predictions = torch.argmax(outputs.logits, dim=1)
        predicted_labels.extend(predictions.cpu().numpy())

# Write predictions to file
with open("results/predicted_labels.txt", "w") as f:
    for label in predicted_labels:
        f.write(str(label) + "\n")
