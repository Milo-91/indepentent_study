model_path = '../model/vicuna-7b-v1.5.Q8_0.gguf'
record_files_folder = 'record'
file_name = '{file_path}/record_crosswords_{idx}.txt'
json_file_name = '{file_path}/tree_crosswords_{idx}.json'
all_json_file_name = '{file_path}/tree_crosswords_all.json'
data_path_crosswords = 'data/mini0505.json'
image_folder = 'crosswords_image'
max_tokens = 1024
temperature = 0.7
n_ctx = 2048
n_gpu_layers = -1
question_sets = 1
initial_idx = 0
b = 3
T = 10
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
    idx = 0
    idx = initial_idx