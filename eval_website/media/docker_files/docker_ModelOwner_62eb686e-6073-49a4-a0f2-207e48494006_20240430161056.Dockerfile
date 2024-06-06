FROM nvcr.io/nvidia/pytorch:24.03-py3
RUN apt update && apt install -y
RUN apt-get -y install git-lfs
RUN git lfs install

