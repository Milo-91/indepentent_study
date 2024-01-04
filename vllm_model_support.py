from vllm import LLM

llm = LLM(model = 'teknium/OpenHermes-2.5-Mistral-7B')  # Name or path of your model
output = llm.generate("Hello, my name is")
print(output)