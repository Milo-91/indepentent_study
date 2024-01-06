import regex
from transformers import AutoModelForCausalLM, AutoTokenizer

from rellm import complete_re

model = AutoModelForCausalLM.from_pretrained("WizardLM/WizardMath-7B-V1.1")
model = model.to("cuda")
tokenizer = AutoTokenizer.from_pretrained("WizardLM/WizardMath-7B-V1.1")

k = 5

propose_prompt = '''Input: 2 8 8 14
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

value_prompt = '''Evaluate if given numbers can reach 24 (sure/likely/impossible)
10 14
10 + 14 = 24
sure
11 12
11 + 12 = 23
12 - 11 = 1
11 * 12 = 132
11 / 12 = 0.91
impossible
4 4 10
4 + 4 + 10 = 8 + 10 = 18
4 * 10 - 4 = 40 - 4 = 36
(10 - 4) * 4 = 6 * 4 = 24
sure
4 9 11
9 + 11 + 4 = 20 + 4 = 24
sure
5 7 8
5 + 7 + 8 = 12 + 8 = 20
(8 - 5) * 7 = 3 * 7 = 21
I cannot obtain 24 now, but numbers are within a reasonable range
likely
5 6 6
5 + 6 + 6 = 17
(6 - 5) * 6 = 1 * 6 = 6
I cannot obtain 24 now, but numbers are within a reasonable range
likely
10 10 11
10 + 10 + 11 = 31
(11 - 10) * 10 = 10
10 10 10 are all too big
impossible
1 3 3
1 * 3 * 3 = 9
(1 + 3) * 3 = 12
1 3 3 are all too small
impossible
24
sure
10
impossible
{input}
'''

cot_final = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24. Each step, you are only allowed to choose two of the remaining numbers to obtain a new number.
Input: 4 4 6 8
Steps:
4 + 8 = 12 (left: 4 6 12)
6 - 4 = 2 (left: 2 12)
2 * 12 = 24 (left: 24)
Answer: (6 - 4) * (4 + 8) = 24
Input: 2 9 10 12
Steps:
12 * 2 = 24 (left: 9 10 24)
10 - 9 = 1 (left: 1 24)
24 * 1 = 24 (left: 24)
Answer: (12 * 2) * (10 - 9) = 24
Input: 4 9 10 13
Steps:
13 - 10 = 3 (left: 3 4 9)
9 - 3 = 6 (left: 4 6)
4 * 6 = 24 (left: 24)
Answer: 4 * (9 - (13 - 10)) = 24
Input: 1 4 8 8
Steps:
8 / 4 = 2 (left: 1 2 8)
1 + 2 = 3 (left: 3 8)
3 * 8 = 24 (left: 24)
Answer: (1 + 8 / 4) * 8 = 24
Input: 5 5 5 9
Steps:
5 + 5 = 10 (left: 5 9 10)
10 + 5 = 15 (left: 9 15)
15 + 9 = 24 (left: 24)
Answer: ((5 + 5) + 5) + 9 = 24
Input: {input}
'''

propose_pattern = r"[0-9]+[\+\-\*\/ ]*[0-9]+[\s]*=[\s]*[0-9]+[\s]*\(left:([0-9\s]+)\)"
pattern_compile = regex.compile(propose_pattern, regex.MULTILINE)
print(pattern_compile)
output = complete_re(tokenizer=tokenizer, 
                     model=model, 
                     prompt=propose_prompt.format(input = '1 1 4 6', k = k),
                     pattern=pattern_compile,
                     do_sample=True,
                     max_new_tokens = 1024,
                     temperature = 0.7)
print(output)

value_pattern = r"[\w|\W]*((?:sure)|(?:likely)|(?:impossible))$"
pattern_compile = regex.compile(value_pattern)
print(pattern_compile)
output = complete_re(tokenizer=tokenizer, 
                     model=model, 
                     prompt=value_prompt.format(input = '2 4 6'),
                     pattern=pattern_compile,
                     do_sample=True,
                     max_new_tokens = 1024,
                     temperature = 0.7)
print(output)

cot_pattern = r"^Answer:[\D]*([\d]+)[\D]*([\d]+)[\D]*([\d]+)[\D]*([\d]+)[\D]*= 24$"
pattern_compile = regex.compile(cot_pattern)
print(pattern_compile)
output = complete_re(tokenizer=tokenizer, 
                     model=model, 
                     prompt=cot_final.format(input = "4 5 6 10\nSteps:\n4 * 5 = 20 (left: 6 10 20)\n10 - 6 = 4 (left: 4 20)\n4 + 20 = 24 (left: 24)\n"),
                     pattern=pattern_compile,
                     do_sample=True,
                     max_new_tokens = 1024,
                     temperature = 0.7)
print(output)