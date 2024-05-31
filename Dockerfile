FROM nvcr.io/nvidia/pytorch:24.03-py3
RUN apt update && apt install -y
RUN apt-get -y install git-lfs
RUN git lfs install
RUN wget https://gist.githubusercontent.com/trajore/3fbd487370b6eecc7366b7b86471d6db/raw/a7f926283ed4a1acb718820716076a5bac8ceeff/requirements.txt
RUN pip install -r requirements.txt

