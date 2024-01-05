from vllm import LLM

llm = LLM(model = 'WizardLM/WizardMath-7B-V1.1')  # Name or path of your model
prompt_template = '"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:"
'
output = llm.generate(prompt_template.format(instruction = "Hello, my name is"))
print(output)