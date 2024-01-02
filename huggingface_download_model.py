from huggingface_hub import hf_hub_download, login

login(token = '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')

hf_hub_download(
    repo_id = 'TheBloke/vicuna-7B-v1.5-GGUF',
    filename = 'vicuna-7b-v1.5.Q8_0.gguf',
    local_dir = 'models'
)