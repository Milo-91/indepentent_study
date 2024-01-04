from vllm import LLM

llm = LLM(model = 'WizardLM/WizardMath-13B-V1.0')  # Name or path of your model
output = llm.generate("Hello, my name is")
print(output)