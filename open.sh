#!/bin/bash

apt update
apt -y upgrade
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_CUBLAS=on" pip install llama-cpp-python
pip install pandas
pip install llama-index
pip install lm-format-enforcer
pip install graphviz
pip install huggingface_hub
apt -y install graphviz
pip install vllm
pip install accelerate
git config --global user.name "Milo-91"
git config --global user.email "milolin9112@gmail.com"
git clone https://github.com/Milo-91/rellm
# python3 huggingface_download_model.py