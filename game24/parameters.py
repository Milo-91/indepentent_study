# model_path = '../models/llemma_7b.Q8_0.gguf'
model_path = '../models/vicuna-13b-v1.5.Q8_0.gguf'
record_files_folder = 'record'
file_name = '{file_path}/record_game24_{idx}.txt'
json_file_name = '{file_path}/tree_game24_{idx}.json'
all_json_file_name = '{file_path}/all_tree_game24.json'
data_path_game24 = 'data/24.csv'
image_folder = 'game24_image'
max_tokens = 1024
temperature = 0.7
n_ctx = 2048
n_gpu_layers = -1
question_sets = 2
initial_idx = 0
b = 3
T = 3
k = 5

id = 0
idx = 0

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
