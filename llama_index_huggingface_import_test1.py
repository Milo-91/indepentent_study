from llama_index.llms.huggingface import HuggingFaceLLM
import lmformatenforcer
import re

from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)

llm = HuggingFaceLLM(
    model_name = "llemma_7b",
    max_new_tokens = 2048,
    model_kwargs={},
    generate_kwargs={"temperature": 0.7, "do_sample": True},
)

regex = r'"Hello, my name is (?P<name>[a-zA-Z]*)\. I was born in (?P<hometown>[a-zA-Z]*). Nice to meet you!"'
'''
regex_parser = lmformatenforcer.RegexParser(regex)
lm_format_enforcer_fn = build_lm_format_enforcer_function(llm, regex_parser)
with activate_lm_format_enforcer(llm, lm_format_enforcer_fn):
    output = llm.complete(
        "Here is a way to present myself, if my name was John and I born in Boston: "
    )
'''
output = llm.complete("1+2=?")
print(output)
# print(re.match(regex, output.text).groupdict())