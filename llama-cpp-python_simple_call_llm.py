from llama_cpp import Llama

model_path = ''
max_tokens = 1024
prompt = ''

llm = Llama(model_path = model_path)
output = llm(
    prompt, 
    max_tokens = max_tokens,
    stop = ["Q:", "\n"],
)

print(output) 