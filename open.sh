#!/bin/bash

apt -y update
apt upgrade
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_CUBLAS=on" pip install llama-cpp-python
pip install pandas
pip install llama-index
pip install lm-format-enforcer
pip install graphviz
apt install -y graphviz
git config --global user.name "Milo-91"
git config --global user.email "milolin9112@gmail.com"