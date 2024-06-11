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

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

#command line arguments
import sys
access_token = sys.argv[1]

#access_token=""
# Load the LLaMA 2 7B model and tokenizer from Hugging Face
model_name = "meta-llama/Llama-2-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name,token=access_token)
model = AutoModelForCausalLM.from_pretrained(model_name,token=access_token)
model.to("cuda")  # Move the model to GPU

# Load the LAMBADA dataset
dataset = load_dataset("cimec/lambada")

# Function to generate predictions
def generate_last_word(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")  # Move inputs to GPU
    outputs = model.generate(**inputs, max_length=inputs['input_ids'].shape[1] + 1)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    last_word = generated_text.split()[-1]
    return last_word

# Evaluate the model on the LAMBADA dataset
results = []
total_examples = len(dataset['test'])
correct_predictions = 0

for i, example in enumerate(dataset['test']):
    text = example['text']
    # Split the text into prompt and the last word (target)
    prompt = " ".join(text.split()[:-1])
    ground_truth = text.split()[-1]
    generated_last_word = generate_last_word(prompt)
    
    # Check if the generated last word matches the ground truth
    is_correct = generated_last_word == ground_truth
    
    if is_correct:
        correct_predictions += 1
    
    results.append({
        "prompt": prompt,
        "ground_truth": ground_truth,
        "generated_last_word": generated_last_word,
        "is_correct": is_correct
    })
    
    # Print progress
    print(f"Processed {i + 1}/{total_examples} examples", end="\r")

# Calculate the accuracy
accuracy = correct_predictions / total_examples
print(f"\nAccuracy: {accuracy:.2f}")

# Optionally, print some results
for result in results[:5]:
    print("\nPrompt:\n", result["prompt"])
    print("Ground Truth:\n", result["ground_truth"])
    print("Generated Last Word:\n", result["generated_last_word"])
    print("Is Correct:", result["is_correct"])
