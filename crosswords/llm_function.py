from openai import OpenAI
from llama_cpp import Llama
import parameters
import lmformatenforcer
from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)
from llama_index.llms import LlamaCPP

def get_llm():
    # llama-cpp
    llm = Llama(model_path = parameters.model_path, n_ctx = parameters.n_ctx, n_gpu_layers = parameters.n_gpu_layers)

    # openai
    '''
    llm = OpenAI(
        api_key = parameters.OPENAI_API_KEY,
    )
    '''
    # llama_index (llama-cpp)
    '''
    llm = LlamaCPP(
        model_path = parameters.model_path,
        temperature = parameters.temperature,
        max_new_tokens = parameters.max_tokens,
        context_window = parameters.n_ctx,
        generate_kwargs={},
        model_kwargs={"n_gpu_layers": parameters.n_gpu_layers},
        verbose = True,
    )
    '''
    return llm


def call_llm(llm, question, pattern_format = None):
    # llama-cpp
    
    response = llm(
            question,
            max_tokens = parameters.max_tokens,
        )
    output = response['choices'][0]['text']
    
    
    # openai
    '''
    response = llm.chat.completions.create(
        model = 'gpt-4-0613',
        temperature = parameters.temperature,
        messages = [
            {
                'role': 'user',
                'content': question,
            }
        ]
    )
    output = response.choices[0].message.content
    '''
    # llama_index
    '''
    regex_parser = lmformatenforcer.RegexParser(pattern_format)
    lm_format_enforcer_fn = build_lm_format_enforcer_function(llm, regex_parser)
    with activate_lm_format_enforcer(llm, lm_format_enforcer_fn):
        response = llm.complete(question)
    output = response.text
    '''
    return output
    
