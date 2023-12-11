model_path = '../openhermes-2.5-neural-chat-7b-v3-1-7b.Q8_0.gguf'
file_name = 'record_game24.txt'
max_tokens = 1024
temperature = 0.7
n_ctx = 2048
n_gpu_layers = -1
OPENAI_API_KEY = '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'

b = 3
T = 3
k = 5

id = 0

def increase_id():
    global id
    id += 1