#!/usr/bin/env python
import torch
from torch import nn
import numpy as np
from torch.optim import Adam
from tqdm import tqdm
from transformers import BertTokenizer, BertModel
from datasets import load_dataset

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load pre-trained BERT tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-cased")

# Load SST-2 dataset
sst2_train = load_dataset("stanfordnlp/sst2", split="train")
sst2_val = load_dataset("stanfordnlp/sst2", split="validation")
sst2_test = load_dataset("stanfordnlp/sst2", split="test")


class Dataset(torch.utils.data.Dataset):
    def __init__(self, df):
        self.labels = [d["label"] for d in df]
        self.texts = [
            tokenizer(
                d["sentence"],
                padding="max_length",
                max_length=128,
                truncation=True,
                return_tensors="pt",
            )
            for d in df
        ]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        batch_texts = self.texts[idx]
        batch_labels = torch.tensor(self.labels[idx])
        return batch_texts, batch_labels


class BertClassifier(nn.Module):
    def __init__(self, num_classes, dropout=0.5):
        super(BertClassifier, self).__init__()
        self.bert = BertModel.from_pretrained("bert-base-cased")
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, num_classes)

    def forward(self, input_id, mask):
        _, pooled_output = self.bert(
            input_ids=input_id, attention_mask=mask, return_dict=False
        )
        dropout_output = self.dropout(pooled_output)
        output = self.linear(dropout_output)
        return output


def train(model, train_data, val_data, learning_rate, epochs):
    train_dataset = Dataset(train_data)
    val_dataset = Dataset(val_data)

    train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=8, shuffle=True)
    val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=8)

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=learning_rate)

    model.to(device)

    for epoch_num in range(epochs):
        total_acc_train = 0
        total_loss_train = 0

        model.train()
        for train_input, train_label in tqdm(train_dataloader, desc=f"Training Epoch {epoch_num+1}/{epochs}"):
            train_label = train_label.to(device)
            mask = train_input["attention_mask"].squeeze(1).to(device)
            input_id = train_input["input_ids"].squeeze(1).to(device)

            optimizer.zero_grad()
            output = model(input_id, mask)
            batch_loss = criterion(output, train_label)
            batch_loss.backward()
            optimizer.step()

            total_loss_train += batch_loss.item()
            acc = (output.argmax(dim=1) == train_label).sum().item()
            total_acc_train += acc

        model.eval()
        total_acc_val = 0
        total_loss_val = 0

        with torch.no_grad():
            for val_input, val_label in tqdm(val_dataloader, desc="Validation"):
                val_label = val_label.to(device)
                mask = val_input["attention_mask"].squeeze(1).to(device)
                input_id = val_input["input_ids"].squeeze(1).to(device)

                output = model(input_id, mask)
                batch_loss = criterion(output, val_label)
                total_loss_val += batch_loss.item()
                acc = (output.argmax(dim=1) == val_label).sum().item()
                total_acc_val += acc

        print(
            f"Epochs: {epoch_num + 1} | Train Loss: {total_loss_train / len(train_dataloader):.3f} | "
            f"Train Accuracy: {total_acc_train / len(train_dataset):.3f} | "
            f"Val Loss: {total_loss_val / len(val_dataloader):.3f} | "
            f"Val Accuracy: {total_acc_val / len(val_dataset):.3f}"
        )

    return model


def evaluate(model, data):
    dataloader = torch.utils.data.DataLoader(Dataset(data), batch_size=1)
    model.to(device)
    model.eval()

    correct_predictions = 0

    with torch.no_grad():
        for input_data, labels in tqdm(dataloader, desc="Evaluating"):
            labels = labels.to(device)
            mask = input_data["attention_mask"].squeeze(1).to(device)
            input_ids = input_data["input_ids"].squeeze(1).to(device)

            outputs = model(input_ids, mask)
            predictions = outputs.argmax(dim=1)
            correct_predictions += (predictions == labels).sum().item()


EPOCHS = 3
model = BertClassifier(2)  # Change the number of classes to 2
LR = 2e-5

# Train model
trained_model = train(model, sst2_train, sst2_val, LR, EPOCHS)

# Evaluate model
evaluate(trained_model, sst2_val)
evaluate(trained_model, sst2_test)
# Save model
torch.save(trained_model.state_dict(), "model_sst2_finetuned.pth")

# Load model
# model = BertClassifier(2)
# model.load_state_dict(torch.load("model_sst2_finetuned.pth"))
# model.to(device)
# evaluate(model, sst2_val)