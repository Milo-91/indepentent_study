model_path = 'vicuna-7b-v1.5.Q8_0.gguf'
file_name = 'record_game24_{idx}.txt'
json_file_name = 'tree_game24.json'
data_path_game24 = 'data/24.csv'
image_folder = 'game24_image'
max_tokens = 1024
temperature = 0.7
n_ctx = 2048
n_gpu_layers = -1
OPENAI_API_KEY = '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'
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
    idx = 0
