from vllm import LLM, SamplingParams
import re
import lmformatenforcer
from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)
from typing import Union, List, Optional
from lmformatenforcer import CharacterLevelParser, RegexParser
from lmformatenforcer.integrations.vllm import build_vllm_logits_processor, build_vllm_token_enforcer_tokenizer_data
import time

ListOrStrList = Union[str, List[str]]

def vllm_with_character_level_parser(prompt: ListOrStrList, tokenizer_data, parser: Optional[CharacterLevelParser] = None) -> ListOrStrList:
        
    sampling_params = SamplingParams(temperature = 0.7, max_tokens = 2048)
    if parser:
        logits_processor = build_vllm_logits_processor(tokenizer_data, parser)
        sampling_params.logits_processors = [logits_processor]
    # Note on batched generation:
    # For some reason, I achieved better batch performance by manually adding a loop similar to this:
    # https://github.com/vllm-project/vllm/blob/main/examples/llm_engine_example.py,
    # I don't know why this is faster than simply calling llm.generate() with a list of prompts, but it is from my tests.
    # However, this demo focuses on simplicity, so I'm not including that here.
    results = llm.generate(prompt, sampling_params=sampling_params)
    if isinstance(prompt, str):
        return results[0].outputs[0].text
    else:
        return [result.outputs[0].text for result in results]

model = "MathLLM/MathCoder-L-7B"

k = 5
pattern = r"-?[0-9\.]+[\+\-\*\/ ]*-?[0-9\.]+[\s]*=[\s]*-?[0-9\.]+"
patterns = '\n'.join([pattern for i in range(k)])

propose_prompt = '''Generate only one set of below output
Input: 2 8 8 14
8 Possible next steps:
2 + 8 = 10
8 / 2 = 4
14 + 2 = 16
2 * 8 = 16
8 - 2 = 6
14 - 8 = 6
14 /  2 = 7
14 - 2 = 12

Input: 2 8 14
5 Possible next steps:
2 + 8 = 10
14 - 8 = 6
14 + 2 = 16
8 / 2 = 4
2 - 8 = -6

Input: 10 14
3 Possible next steps:
10 + 14 = 24
10 - 14 = -4
10 * 14 = 140

Input: {input}
{k} Possible next steps:
'''

value_pattern = r"[\w|\W]*((?:sure)|(?:likely)|(?:impossible))"
value_prompt = '''Evaluate if given numbers can reach 24 (sure/likely/impossible)
below are 10 examples, and generate only one set of below output
in the end must be sure, likely, or impossible
Input: 10 14
Analysis:
10 + 14 = 24
sure

Input: 11 12
Analysis:
11 + 12 = 23
12 - 11 = 1
11 * 12 = 132
11 / 12 = 0.91
impossible

Input: 4 4 10
Analysis:
4 + 4 + 10 = 8 + 10 = 18
4 * 10 - 4 = 40 - 4 = 36
(10 - 4) * 4 = 6 * 4 = 24
sure

Input: 4 9 11
Analysis:
9 + 11 + 4 = 20 + 4 = 24
sure

Input: 5 7 8
Analysis:
5 + 7 + 8 = 12 + 8 = 20
(8 - 5) * 7 = 3 * 7 = 21
I cannot obtain 24 now, but the numbers are within a reasonable range
likely

Input: 5 6 6
Analysis:
5 + 6 + 6 = 17
(6 - 5) * 6 = 1 * 6 = 6
I cannot obtain 24 now, but the numbers are within a reasonable range
likely

Input: 10 10 11
Analysis:
10 + 10 + 11 = 31
(11 - 10) * 10 = 10
10 10 10 are all too big
impossible

Input: 1 3 3
Analysis:
1 * 3 * 3 = 9
(1 + 3) * 3 = 12
1 3 3 are all too small
impossible

Input: 24
Analysis:
24 is equal to 24
sure

Input: 10
Analysis:
10 is not equal to 24
impossible

Input: {input}
Analysis:
'''


llm = LLM(model = model, trust_remote_code = True)

tokenizer_data = build_vllm_token_enforcer_tokenizer_data(llm)

start_time = time.time()
result = vllm_with_character_level_parser(propose_prompt.format(input = '1 1 4 6', k = k), tokenizer_data, RegexParser(patterns))
end_time = time.time()
print(result)
print(end_time - start_time)

start_time = time.time()
result = vllm_with_character_level_parser(value_prompt.format(input = '0 4 6'), tokenizer_data, RegexParser(value_pattern))
end_time = time.time()
print(result)
print(end_time - start_time)

'''
outputs = llm.generate(question.format(input = '1 1 4 6', k = k), sampling_params)

# print the outputs
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"prompt: {prompt!r}, Generated text: {generated_text!r}")
'''