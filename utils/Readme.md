# Utils

This directory contains utility scripts for downloading and processing datasets and models. The scripts are designed to be run from the command line.

## TTP_TEE_files

Refer to the [Readme.md](/utils/TTP_TEE_files/Readme.md) file in the TTP_TEE_files directory for more information on the files in this directory.

## Files

1. `remove_indicxnli.py`: This script loads the IndicXNLI dataset, removes the 'label' column, gets the test split, and saves it to disk.

2. `remove_sst2.py`: This script loads the SST2 dataset, removes the 'label' column, gets the test split, and saves it to disk.

3. `remove_humaneval.py`: This script loads the HumanEval dataset, removes the 'canonical_solution' column, gets the test split, and saves it to disk.

4. `datasets_download.py`: This script downloads a specified dataset or all available datasets. It also processes the IndicXNLI dataset to strip leading and trailing spaces from the 'premise' and 'hypothesis' fields.

5. `model_download.py`: This script downloads a specified model or all available models. It handles different types of models, including causal language models and masked language models. It also handles a special case for the 'hf_hub:timm/vgg16.tv_in1k' model.



**Note**: The label remove files are used to remove the label column from the dataset and save the test split to disk. This is done to ensure that in the case of Evaluation type 1 and 2 the model owner does not have access to the labels of the test set. The dataset owner checks the model owner's predictions against the test set and provides the final score.

## Usage

For each script, you can run it from the command line with the name of the dataset or model as an argument. For example:

```bash
python remove_indicxnli.py
python datasets_download.py openai_humaneval
python model_download.py google-bert/bert-base-cased
```

You can also use the `--all` flag to download all available datasets or models:

```bash
python datasets_download.py --all
python model_download.py --all
```

## License

This project is licensed under the MIT License. See the individual Python files for the full license text.