from openai import OpenAI
from llama_cpp import Llama
from vllm import LLM, SamplingParams
import parameters
import lmformatenforcer
from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)
from llama_index.llms import LlamaCPP
from llama_index.llms.vllm import Vllm
from typing import Union, List, Optional
from lmformatenforcer import CharacterLevelParser, RegexParser
from lmformatenforcer.integrations.vllm import build_vllm_logits_processor, build_vllm_token_enforcer_tokenizer_data
ListOrStrList = Union[str, List[str]]

def vllm_with_character_level_parser(llm, prompt: ListOrStrList, tokenizer_data, parser: Optional[CharacterLevelParser] = None) -> ListOrStrList:   
    sampling_params = SamplingParams(temperature = parameters.temperature, max_tokens = parameters.n_ctx)
    if parser:
        logits_processor = build_vllm_logits_processor(tokenizer_data, parser)
        sampling_params.logits_processors = [logits_processor]

    results = llm.generate(prompt, sampling_params=sampling_params)
    if isinstance(prompt, str):
        return results[0].outputs[0].text
    else:
        return [result.outputs[0].text for result in results]

def get_llm():
    # llama-cpp
    # llm = Llama(model_path = parameters.model_path, n_ctx = parameters.n_ctx, n_gpu_layers = parameters.n_gpu_layers)

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
    # llama_index (vllm)
    '''
    llm = Vllm(
        model = "WizardLM/WizardMath-13B-V1.0",
        dtype = "float16",
        tensor_parallel_size = 1,
        temperature = parameters.temperature,
        max_new_tokens = parameters.max_tokens,
        vllm_kwargs={
            "swap_space": 1,
            "gpu_memory_utilization": 0.7,
            "max_model_len": parameters.n_ctx,
        },
    )
    '''

    # vllm
    
    llm = LLM(model = parameters.huggingface_model_path, trust_remote_code = True)

    
    return llm


def call_llm(llm, question, pattern_format):
    # llama-cpp
    '''
    response = llm(
            question,
            max_tokens = parameters.max_tokens,
        )
    output = response['choices'][0]['text']
    '''
    
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
    # llama_index (llama-cpp)
    '''
    regex_parser = lmformatenforcer.RegexParser(pattern_format)
    lm_format_enforcer_fn = build_lm_format_enforcer_function(llm, regex_parser)
    with activate_lm_format_enforcer(llm, lm_format_enforcer_fn):
        response = llm.complete(question)
    output = response.text
    '''
    # llama_index (vllm)
    '''
    output = llm.complete(question).text
    '''

    # vllm

    tokenizer_data = build_vllm_token_enforcer_tokenizer_data(llm)
    output = vllm_with_character_level_parser(llm, question, tokenizer_data, RegexParser(pattern_format))

    
    return output