import re
import lmformatenforcer
from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)
from llama_index.llms import LlamaCPP


model_path = 'vicuna-7b-v1.5.Q8_0.gguf'
max_tokens = 2048
k = 5
prompt = '''Input: 2 8 8 14
8 Possible next steps:
2 + 8 = 10 (left: 8 10 14)
8 / 2 = 4 (left: 4 8 14)
14 + 2 = 16 (left: 8 8 16)
2 * 8 = 16 (left: 8 14 16)
8 - 2 = 6 (left: 6 8 14)
14 - 8 = 6 (left: 2 6 8)
14 / 2 = 7 (left: 7 8 8)
14 - 2 = 12 (left: 8 8 12)
Input: {input}
{k} Possible next steps:
'''

llm = LlamaCPP(
    # optionally, you can set the path to a pre-downloaded model instead of model_url
    model_path = model_path,
    temperature = 0.7,
    max_new_tokens = 2048,
    # llama2 has a context window of 4096 tokens, but we set it lower to allow for some wiggle room
    context_window = 2048,# n_ctx
    # kwargs to pass to __call__()
    generate_kwargs={},
    # kwargs to pass to __init__()
    # set to at least 1 to use GPU
    model_kwargs={"n_gpu_layers": -1},
    # transform inputs into Llama2 format
    verbose=True,
)

regex_parser = lmformatenforcer.RegexParser(patterns)
lm_format_enforcer_fn = build_lm_format_enforcer_function(llm, regex_parser)
with activate_lm_format_enforcer(llm, lm_format_enforcer_fn):
    output = llm.complete(prompt.format(input = '1 1 4 6', k = k))

print(output)