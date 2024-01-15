from vllm import LLM, SamplingParams
from typing import Union, List, Optional
from lmformatenforcer import CharacterLevelParser, RegexParser
from lmformatenforcer.integrations.vllm import build_vllm_logits_processor, build_vllm_token_enforcer_tokenizer_data
ListOrStrList = Union[str, List[str]]
import re
import time

def vllm_with_character_level_parser(llm, prompt: ListOrStrList, tokenizer_data, temperature, parser: Optional[CharacterLevelParser] = None) -> ListOrStrList:   
    sampling_params = SamplingParams(temperature = temperature, max_tokens = 2048)
    if parser:
        logits_processor = build_vllm_logits_processor(tokenizer_data, parser)
        sampling_params.logits_processors = [logits_processor]

    results = llm.generate(prompt, sampling_params=sampling_params)
    if isinstance(prompt, str):
        return results[0].outputs[0].text
    else:
        return [result.outputs[0].text for result in results]

value_prompt = '''Evaluate if given numbers can reach 24 (sure/likely/impossible)
you can generate only one set of the below examples according to the Input
Output must be sure, likely, or impossible, choose one
Input: 4 4 10
Analysis:
4 + 4 + 10 = 8 + 10 = 18
4 * 10 - 4 = 40 - 4 = 36
(10 - 4) * 4 = 6 * 4 = 24
Output: sure (4 4 10)

Input: 4 9 11
Analysis:
9 + 11 + 4 = 20 + 4 = 24
Output: sure (4 9 11)

Input: 5 7 8
Analysis:
5 + 7 + 8 = 12 + 8 = 20
(8 - 5) * 7 = 3 * 7 = 21
I cannot obtain 24 now, but the numbers are within a reasonable range
Output: likely (5 7 8)

Input: 5 6 6
Analysis:
5 + 6 + 6 = 17
(6 - 5) * 6 = 1 * 6 = 6
I cannot obtain 24 now, but the numbers are within a reasonable range
Output: likely (5 6 6)

Input: 10 10 11
Analysis:
10 + 10 + 11 = 31
(11 - 10) * 10 = 10
10 10 10 are all too big
Output: impossible (10 10 11)

Input: 1 3 3
Analysis:
1 * 3 * 3 = 9
(1 + 3) * 3 = 12
1 3 3 are all too small
Output: impossible (1 3 3)

Input: 10 14
Analysis:
10 + 14 = 24
Output: sure (10 14)

Input: 11 12
Analysis:
11 + 12 = 23
12 - 11 = 1
11 * 12 = 132
11 / 12 = 0.91
Output: impossible (11 12)

Input: 24
Analysis:
24 is equal to 24
Output: sure (24)

Input: 10
Analysis:
10 is not equal to 24
Output: impossible (10)

Input: {input}
'''

input = '3 8'
question = value_prompt.format(input = input)
temperature = 0
pattern = r"Analysis:[\w|\W]*[\n]Output: ((?:sure)|(?:likely)|(?:impossible))\(-?[\d\.\s]+\)"
pattern = r"[\w\W]*"
llm = LLM(model = 'TheBloke/OpenHermes-2.5-Mistral-7B-GPTQ', trust_remote_code = True, enforce_eager = True)

start_time = time.time()
tokenizer_data = build_vllm_token_enforcer_tokenizer_data(llm)
output = vllm_with_character_level_parser(llm, question, tokenizer_data, temperature, RegexParser(pattern))
# sampling_params = SamplingParams(temperature = temperature, max_tokens = 2048)
# results = llm.generate(question, sampling_params=sampling_params)
# output = results[0].outputs[0].text
end_time = time.time()
print(output)
print(end_time - start_time)

output_pattern = r"Output: ((?:sure)|(?:likely)|(?:impossible)) \({input}\)".format(input = input)
print(output_pattern)
match = re.search(output_pattern, output)
if match:
    print(match.group())
    print(match.group(1))
