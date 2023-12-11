from openai import OpenAI
from llama_cpp import Llama
import parameters

def get_llm():
    #llm = Llama(model_path = parameters.model_path, n_ctx = parameters.n_ctx, n_gpu_layers = parameters.n_gpu_layers)
    llm = OpenAI(
        api_key = parameters.OPENAI_API_KEY,
    )
    return llm

def call_llm(llm, question):
    '''
    response = llm(
            input_string,
            max_tokens = parameters.max_tokens,
        )
    '''
    response = llm.chat.completions.create(
        model = 'gpt-3.5-turbo-1106',
        temperature = parameters.temperature,
        messages = [
            {
                'role': 'user',
                'content': question,
            }
        ]
    )
    return response
    