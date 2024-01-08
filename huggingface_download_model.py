from huggingface_hub import hf_hub_download, login

login(token = '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')


hf_hub_download(
    repo_id = 'TheBloke/OpenHermes-2.5-Mistral-7B-GGUF',
    filename = 'openhermes-2.5-mistral-7b.Q8_0.gguf',
    local_dir = 'models'
)

'''
hf_hub_download(
    repo_id = 'TheBloke/vicuna-13B-v1.5-GGUF',
    filename = 'vicuna-13b-v1.5.Q8_0.gguf',
    local_dir = 'models'
)

hf_hub_download(
    repo_id = 'TheBloke/vicuna-7B-v1.5-GGUF',
    filename = 'vicuna-7b-v1.5.Q8_0.gguf',
    local_dir = 'models'
)

hf_hub_download(
    repo_id = 'TheBloke/llemma_7b-GGUF',
    filename = 'llemma_7b.Q8_0.gguf',
    local_dir = 'models'
)
'''