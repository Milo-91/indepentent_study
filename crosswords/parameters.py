# llamacpp
repo_id = ''
model_name = 'vicuna-7b-v1.5.Q8_0.gguf'
local_dir = '../models'
model_path = local_dir + '/' + model_name
# vllm
huggingface_model_path = 'TheBloke/OpenHermes-2.5-Mistral-7B-GPTQ'
# openai
openai_model = 'gpt-3.5-turbo-1106'

record_files_folder = 'record'
file_name = '{file_path}/record_crosswords_{idx}.txt'
json_file_name = '{file_path}/tree_crosswords_{idx}.json'
all_json_file_name = '{file_path}/tree_crosswords_all.json'
acc_file_name = '{file_path}/acc_info_crosswords.txt'
data_path_crosswords = 'data/mini0505.json'
image_folder = 'crosswords_image'
max_tokens = 1024
generator_temperature = 0.5
evaluator_temperature = 0
n_ctx = 2048
n_gpu_layers = -1
question_sets = 1
initial_idx = 0
b = 3
T = 10
k = 5

id = 0
idx = 0

# (tot-dfs, dfs+sd)
method = 'tot-dfs'
model_import_method = 'openai'
with_lmformatenforcer = False

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
    idx = 0
    idx = initial_idx
