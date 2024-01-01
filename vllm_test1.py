from vllm import LLM, SamplingParams
import re
import lmformatenforcer
from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)

model = "lmsys/vicuna-7b-v1.3"

k = 5
pattern = r"[0-9]+[\s]*[\+\-\*\/][\s]*[0-9]+[\s]*=[\s]*[0-9]*[\s]*\(left:[0-9\s]*\)"
patterns = '\n'.join([pattern for i in range(k)])

sampling_params = SamplingParams(temperature = 0.8, max_tokens = 2048, top_k = 5)

question = '''Input: 2 8 8 14
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

llm = LLM(model = model)
outputs = llm.generate(question.format(input = '1 1 4 6', k = k), sampling_params)

# print the outputs
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"prompt: {prompt!r}, Generated text: {generated_text!r}")