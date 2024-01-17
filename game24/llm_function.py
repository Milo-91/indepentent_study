import parameters
import os
from typing import Union, List, Optional
ListOrStrList = Union[str, List[str]]

if parameters.model_import_method == 'openai':
    from dotenv import load_dotenv
    from openai import OpenAI
if parameters.model_import_method == 'llamacpp':
    from llama_cpp import Llama
if parameters.model_import_method == 'vllm':
    from vllm import LLM, SamplingParams
if parameters.model_import_method == 'llamaindex':
    from llama_index.prompts.lmformatenforcer_utils import (
        activate_lm_format_enforcer,
        build_lm_format_enforcer_function,
    )
    from llama_index.llms import LlamaCPP
    from llama_index.llms.vllm import Vllm
if parameters.with_lmformatenforcer == True:
    import lmformatenforcer
    from lmformatenforcer import CharacterLevelParser, RegexParser
    from lmformatenforcer.integrations.vllm import build_vllm_logits_processor, build_vllm_token_enforcer_tokenizer_data

completion_tokens = prompt_tokens = 0

def vllm_with_character_level_parser(llm, prompt: ListOrStrList, tokenizer_data, temperature, sampling_params, parser = None) -> ListOrStrList:   
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
    if parameters.model_import_method == 'llamacpp':
        llm = Llama(model_path = parameters.model_path, n_ctx = parameters.n_ctx, n_gpu_layers = parameters.n_gpu_layers)
    
    # openai
    if parameters.model_import_method == 'openai':
        load_dotenv()
        llm = OpenAI(
            api_key = os.getenv("OPENAI_API_KEY"),
        )
    
    # llama_index (llama-cpp)
    if parameters.model_import_method == 'llamaindex':
        llm = LlamaCPP(
            model_path = parameters.model_path,
            temperature = parameters.temperature,
            max_new_tokens = parameters.max_tokens,
            context_window = parameters.n_ctx,
            generate_kwargs={},
            model_kwargs={"n_gpu_layers": parameters.n_gpu_layers},
            verbose = True,
        )
    
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
    if parameters.model_import_method == 'vllm':
        llm = LLM(model = parameters.huggingface_model_path, trust_remote_code = True, enforce_eager = True)
    
    
    return llm


def call_llm(llm, question, pattern_format, temperature):
    # llama-cpp
    if parameters.model_import_method == 'llamacpp':
        response = llm(
                question,
                max_tokens = parameters.max_tokens,
            )
        output = response['choices'][0]['text']
    
    # openai
    if parameters.model_import_method == 'openai':
        response = llm.chat.completions.create(
            model = parameters.openai_model,

            temperature = temperature,
            messages = [
                {
                    'role': 'user',
                    'content': question,
                }
            ]
        )
        output = response.choices[0].message.content
        global completion_tokens, prompt_tokens
        completion_tokens += response.usage.completion_tokens
        prompt_tokens += response.usage.prompt_tokens
    
    # llama_index (llama-cpp)
    if parameters.model_import_method == 'llamaindex':
        regex_parser = lmformatenforcer.RegexParser(pattern_format)
        lm_format_enforcer_fn = build_lm_format_enforcer_function(llm, regex_parser)
        with activate_lm_format_enforcer(llm, lm_format_enforcer_fn):
            response = llm.complete(question)
        output = response.text

    # llama_index (vllm)
    '''
    output = llm.complete(question).text
    '''

    # vllm
    if parameters.model_import_method == 'vllm':    
        sampling_params = SamplingParams(temperature = temperature, max_tokens = parameters.n_ctx)
        if pattern_format != None:
            tokenizer_data = build_vllm_token_enforcer_tokenizer_data(llm)
            output = vllm_with_character_level_parser(llm, question, tokenizer_data, temperature, sampling_params, RegexParser(pattern_format))
        else:
            results = llm.generate(question, sampling_params = sampling_params)
            output = results[0].outputs[0].text

    
    return output


def openai_usage():
    cost = 0
    if parameters.openai_model == 'gpt-3.5-turbo-1106':
        cost = completion_tokens / 1000 * 0.002 + prompt_tokens / 1000 * 0.001
    if parameters.openai_model == 'gpt-4-0613':
        cost = completion_tokens / 1000 * 0.06 + prompt_tokens / 1000 * 0.03
    
    return cost