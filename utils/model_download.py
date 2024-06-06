import argparse
from transformers import AutoTokenizer, AutoModelForMaskedLM , AutoModelForCausalLM
import os
#install timm
import torch
import timm
token = ''
def download_model(model_name):
    if model_name =='hf_hub:timm/vgg16.tv_in1k':
        tokenizer = None
    else:
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
    
    if model_name == 'meta-llama/Llama-2-7b-hf' or model_name == 'ai4bharat/Airavata':
        model = AutoModelForCausalLM.from_pretrained(model_name, token=token)
    elif model_name == 'hf_hub:timm/vgg16.tv_in1k':
        model = timm.create_model(model_name, pretrained=True)
    else:
        model = AutoModelForMaskedLM.from_pretrained(model_name, token=token)
    model_dir = './model_files/{}/'.format(model_name)
    os.makedirs(model_dir, exist_ok=True)
    if model_name== 'hf_hub:timm/vgg16.tv_in1k':
        torch.save(model.state_dict(),model_dir[:]+'vgg16.pth')
    else:
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
    print('Model saved:', model_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', nargs='?', help='Name of the model to download. Choose from: google-bert/bert-base-cased, meta-llama/Llama-2-7b-hf, ai4bharat/Airavata,hf_hub:timm/vgg16.tv_in1k')
    parser.add_argument('--all', action='store_true', help='Download all available models')
    args = parser.parse_args()

    if args.all:
        models=['google-bert/bert-base-cased',
                'meta-llama/Llama-2-7b-hf',
                'ai4bharat/Airavata',
                'hf_hub:timm/vgg16.tv_in1k',]
    elif args.model_name is None:
        parser.print_help()
        exit()
    else:
        models = args.model_name.split(',')

    for model_name in models:
        download_model(model_name.strip())

#usage
# python model_download.py google-bert/bert-base-cased