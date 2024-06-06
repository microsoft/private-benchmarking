# Local Testing

## Running the tests
For running the tests on EzPC, you can use the following command:
```bash EzPC.sh```

For running the tests on TEE/TTP, you can use the following command:
```bash TTP_TEE.sh```

## Hardware Requirements for TEE(Trust Execution Environment)
- Intel SGX enabled machine or AMD SEV enabled machine
- Nvidia H100 Hopper GPU in CC (confidential computing) mode [info](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/HCC-Whitepaper-v1.0.pdf)
- Nvidia H100 Hopper GPU in CC mode is required for running the tests on TEE.

## Hardware Requirements for TTP(Trusted Third Party)
- Nvidia H100 Hopper GPU in CC-off mode [info](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/HCC-Whitepaper-v1.0.pdf)
