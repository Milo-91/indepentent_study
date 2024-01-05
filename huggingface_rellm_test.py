import regex
from transformers import AutoModelForCausalLM, AutoTokenizer

from rellm import complete_re

model = AutoModelForCausalLM.from_pretrained("WizardLM/WizardMath-7B-V1.1")
model = model.to("cuda")
tokenizer = AutoTokenizer.from_pretrained("WizardLM/WizardMath-7B-V1.1")

k = 5

prompt = '''Input: 2 8 8 14
8 Possible next steps:
2 + 8 = 10 (left: 8 10 14)
8 / 2 = 4 (left: 4 8 14)
14 + 2 = 16 (left: 8 8 16)
2 * 8 = 16 (left: 8 14 16)
8 - 2 = 6 (left: 6 8 14)
14 - 8 = 6 (left: 2 6 8)
14 /  2 = 7 (left: 7 8 8)
14 - 2 = 12 (left: 8 8 12)

Input: 2 8 14
3 Possible next steps:
2 + 8 = 10 (left: 10 14)
14 - 8 = 6 (left: 2 6)
14 + 2 = 16 (left: 8 16)

Input: 10 14
3 Possible next steps:
10 + 14 = 24 (left: 24)
10 - 14 = -4 (left: -4)
10 * 14 = 140 (left: 140)

Input: {input}
{k} Possible next steps:
'''
pattern = r"[0-9]+[\s]*[\+\-\*\/][\s]*[0-9]+[\s]*=[\s]*[0-9]*[\s]*\(left:[0-9\s]*\)"
patterns = regex.compile('\n'.join([pattern for i in range(k)]))
print(patterns)
output = complete_re(tokenizer=tokenizer, 
                     model=model, 
                     prompt=prompt.format(input = '1 1 4 6', k = k),
                     pattern=patterns,
                     do_sample=True,
                     max_new_tokens=80)
print(output)