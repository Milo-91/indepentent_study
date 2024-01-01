#!/bin/bash

apt update
apt upgrade
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_CUBLAS=on" pip install llama-cpp-python
pip install pandas
