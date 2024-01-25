# llamacpp
repo_id = 'TheBloke/OpenHermes-2.5-neural-chat-7B-v3-1-7B-GGUF'
model_name = 'openhermes-2.5-neural-chat-7b-v3-1-7b.Q8_0.gguf'
local_dir = '../models'
model_path = local_dir + '/' + model_name
# vllm
huggingface_model_path = 'TheBloke/OpenHermes-2.5-Mistral-7B-GPTQ'
# openai
openai_model = 'gpt-3.5-turbo-1106'

record_files_folder = 'record'
file_name = '{file_path}/record_game24_{idx}.txt'
json_file_name = '{file_path}/tree_game24_{idx}.json'
all_json_file_name = '{file_path}/all_tree_game24.json'
acc_file_name = '{file_path}/acc_info_game24.txt'
data_path_game24 = 'data/24.csv'
image_folder = 'game24_image'
max_tokens = 1024
generator_temperature = 0.5
evaluator_temperature = 0
n_ctx = 2048
n_gpu_layers = -1
question_sets = 100
initial_idx = 901
b = 5
T = 3
k = 5

id = 0
idx = 0
t = 0
method = 'dfs'
model_import_method = 'vllm'
with_lmformatenforcer = True

def increase_id():
    global id
    id += 1

def reset_id():
    global id
    id = 0

def increase_idx():
    global idx
    idx += 1

def reset_idx():
    global idx
    global initial_idx
    idx = initial_idx

def increase_t():
    global t
    t += 1

def decrease_t():
    global t
    t -= 1

def reset_t():
    global t
    t = 0

def set_b(initial_b):
    global b
    b = initial_b