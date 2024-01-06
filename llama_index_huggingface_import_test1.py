from llama_index.llms.huggingface import HuggingFaceLLM
import lmformatenforcer
import re

from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)

llm = HuggingFaceLLM(
    model_name = "EleutherAI/llemma_7b",
    max_new_tokens = 1024,
    model_kwargs={"n_gpu_layers": -1},
    generate_kwargs={"temperature": 0.7},
)

regex = r'"Hello, my name is (?P<name>[a-zA-Z]*)\. I was born in (?P<hometown>[a-zA-Z]*). Nice to meet you!"'

regex_parser = lmformatenforcer.RegexParser(regex)
lm_format_enforcer_fn = build_lm_format_enforcer_function(llm, regex_parser)
with activate_lm_format_enforcer(llm, lm_format_enforcer_fn):
    output = llm.complete(
        "Here is a way to present myself, if my name was John and I born in Boston: "
    )

print(output)
print(re.match(regex, output.text).groupdict())