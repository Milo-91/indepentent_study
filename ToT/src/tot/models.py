import os
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

def gpt(prompt, model="gpt-4", temperature=0.7, max_tokens=1000, n=1, stop=None, idx = None) -> list:
    messages = [{"role": "user", "content": prompt}]
    return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop, idx = idx)
    
def chatgpt(messages, model="gpt-4", temperature=0.7, max_tokens=1000, n=1, stop=None, idx = None) -> list:
    global completion_tokens_4, prompt_tokens_4, completion_tokens_3_5, prompt_tokens_3_5
    outputs = []
    while n > 0:
        cnt = min(n, 20)
        n -= cnt
        res = completions_with_backoff(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop)
        print(res)
        # record.Record_txt(record.record_file_name, f'\nres(n={cnt}): ' + str(res) +'\n\n', idx)
        outputs.extend([choice["message"]["content"] for choice in res["choices"]])
        record.Record_txt(record.debug_file_name, f'\nres(n={cnt}, model={model}): ' + str(res) +'\n\n', idx)
        # log completion tokens
        if model == 'gpt-4':
            completion_tokens_4 += res["usage"]["completion_tokens"]
            prompt_tokens_4 += res["usage"]["prompt_tokens"]
        else:
            completion_tokens_3_5 += res["usage"]["completion_tokens"]
            prompt_tokens_3_5 += res["usage"]["prompt_tokens"]
    return outputs
    
def gpt_usage(backend="gpt-4"):
    global completion_tokens_4, prompt_tokens_4, completion_tokens_3_5, prompt_tokens_3_5
    cost = 0
    if backend == "gpt-4":
        cost += completion_tokens_4 / 1000 * 0.06 + prompt_tokens_4 / 1000 * 0.03
    elif backend == "gpt-3.5-turbo":
        cost += completion_tokens_3_5 / 1000 * 0.002 + prompt_tokens_3_5 / 1000 * 0.0015
    return {"completion_tokens": completion_tokens_4 + completion_tokens_3_5, "prompt_tokens": prompt_tokens_4 + prompt_tokens_3_5, "cost": cost}
