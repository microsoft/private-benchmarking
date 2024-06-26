# Local Testing

## Running the tests
For running the tests on EzPC, you can use the following command:
```bash EzPC.sh```

For running the tests on TEE/TTP, you can use the following command:
```bash TTP_TEE.sh```

**NOTE** : Incase of First Run of these scripts on your machine, It will download the required models and data for the tests. This will take some time depending on your internet speed. Thus for consistent results, it is recommended to run the tests again after the first run.


## Hardware Requirements for TEE(Trust Execution Environment)
- Intel SGX enabled machine or AMD SEV enabled machine
- Nvidia H100 Hopper GPU in CC (confidential computing) mode [info](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/HCC-Whitepaper-v1.0.pdf)
- Nvidia H100 Hopper GPU in CC mode is required for running the tests on TEE.

## Hardware Requirements for TTP(Trusted Third Party)
- Nvidia H100 Hopper GPU in CC-off mode [info](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/HCC-Whitepaper-v1.0.pdf)

## Hardware Requirements for EzPC
- For running Local Tests for EzPC on Hopper you need to have 2 GPUs on the same machine for running party 0 and party 1 on different GPUs and testing locally.
- For running Dealer phase either of the GPUs can be used.
- Please set CUDA_VISIBLE_DEVICES=0 for party 0 and CUDA_VISIBLE_DEVICES=1 for party 1 before running the tests.