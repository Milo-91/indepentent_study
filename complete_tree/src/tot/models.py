import os
import math
import openai
import backoff 
from dotenv import load_dotenv
import tot.record_functions as record

completion_tokens_4 = prompt_tokens_4 = 0
completion_tokens_3_5 = prompt_tokens_3_5 = 0
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")
if api_key != "":
    openai.api_key = api_key
else:
    print("Warning: OPENAI_API_KEY is not set")
    
api_base = os.getenv("OPENAI_API_BASE", "")
if api_base != "":
    print("Warning: OPENAI_API_BASE is set to {}".format(api_base))
    openai.api_base = api_base

@backoff.on_exception(backoff.expo, openai.error.OpenAIError)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

def gpt(prompt, model='gpt-3.5-turbo', temperature=0.7, max_tokens=1000, n=1, stop=None, idx = None, logprobs = False) -> list:
    messages = [{"role": "user", "content": prompt}]
    if model == 'gpt-4':
        record.Record_txt(record.debug_file_name, '\nuse gpt-4\nprompt:\n' + prompt + '\n\n', idx = idx)
    return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop, idx = idx, logprobs = logprobs)

def chatgpt(messages, model='gpt-3.5-turbo', temperature=0.7, max_tokens=1000, n=1, stop=None, idx = None, logprobs = False) -> list:
    global completion_tokens_4, prompt_tokens_4, completion_tokens_3_5, prompt_tokens_3_5
    outputs = []
    if logprobs == False:
        while n > 0:
            cnt = min(n, 20)
            n -= cnt
            res = completions_with_backoff(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop)
            outputs.extend([choice["message"]["content"] for choice in res["choices"]])
            record.Record_txt(record.debug_file_name, '\nuse model: ' + res['model'] + '\n\n', idx = idx)
            # log completion tokens
            if model == 'gpt-4':
                completion_tokens_4 += res["usage"]["completion_tokens"]
                prompt_tokens_4 += res["usage"]["prompt_tokens"]
            elif model == 'gpt-3.5-turbo':
                completion_tokens_3_5 += res["usage"]["completion_tokens"]
                prompt_tokens_3_5 += res["usage"]["prompt_tokens"]
            else:
                record.Record_txt(record.debug_file_name, '\nunknown model\n\n', idx = idx)

        return outputs
    else:
        avg_probs = []
        while n > 0:
            cnt = min(n, 20)
            n -= cnt
            res = completions_with_backoff(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop, logprobs=True)
            outputs.extend([choice["message"]["content"] for choice in res["choices"]])
            record.Record_txt(record.debug_file_name, '\nuse model: ' + res['model'] + '\n\n', idx = idx)
            for r in res['choices']:
                log_list = [log['logprob'] for log in r['logprobs']['content']]
                avg_prob = math.exp(sum(log_list) / len(log_list))
                avg_probs.append(avg_prob)
            # log completion tokens
            if model == 'gpt-4':
                completion_tokens_4 += res["usage"]["completion_tokens"]
                prompt_tokens_4 += res["usage"]["prompt_tokens"]
            elif model == 'gpt-3.5-turbo':
                completion_tokens_3_5 += res["usage"]["completion_tokens"]
                prompt_tokens_3_5 += res["usage"]["prompt_tokens"]
            else:
                record.Record_txt(record.debug_file_name, '\nunknown model\n\n', idx = idx)
                
        return outputs, avg_probs
    
def gpt_usage(backend="gpt-4"):
    global completion_tokens_4, prompt_tokens_4, completion_tokens_3_5, prompt_tokens_3_5
    cost = 0
    if backend == "gpt-4":
        cost += completion_tokens_4 / 1000 * 0.06 + prompt_tokens_4 / 1000 * 0.03
    elif backend == "gpt-3.5-turbo":
        cost += completion_tokens_3_5 / 1000 * 0.002 + prompt_tokens_3_5 / 1000 * 0.0015
    return {"gpt-4 completion_tokens": completion_tokens_4, "gpt-4 prompt_tokens": prompt_tokens_4 , 'gpt-3.5 completion_tokens': completion_tokens_3_5, 'gpt-3.5 prompt_tokens': prompt_tokens_3_5, "cost": cost}
