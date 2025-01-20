from functools import partial
from tot.models import gpt
import tot.record_functions as record
import time

index = 0 # idx

def get_value(task, y, n_evaluate_sample, evaluator_method, cache_value=True):
    value_prompt = task.value_prompt_wrap(y)
    # record.Record_txt(record.record_file_name, '\nvalue prompt: ' + value_prompt + '\n\n', idx = index)
    if 'wrong answer' in y:
        return 0
    if cache_value and value_prompt in task.value_cache:
        # record.Record_txt(record.record_file_name, '\n' + value_prompt + '\nuse cache\n\n', idx = index)
        return task.value_cache[value_prompt]
    if evaluator_method == 'origin':
        value_outputs = gpt(value_prompt, n=n_evaluate_sample, stop=None, idx = index, logprobs = False)
        record.Record_txt(record.debug_file_name, '\nevaluator method: ' + evaluator_method + '\nvalue outputs: ' + str(value_outputs) + '\n\n', idx = index)
        value = task.value_outputs_unwrap(y, value_outputs, evaluator_method)
    elif evaluator_method == 'logprob':
        value_outputs, avg_probs = gpt(value_prompt, n=n_evaluate_sample, stop=None, idx = index, logprobs = True)
        print(avg_probs)
        record.Record_txt(record.debug_file_name, '\nevaluator method: ' + evaluator_method + '\nvalue outputs: ' + str(value_outputs) + '\navg probs: ' + str(avg_probs) + '\n\n', idx = index)
        value = task.value_outputs_unwrap(y, value_outputs, evaluator_method, avg_probs)
    record.Record_txt(record.debug_file_name, 'final value: ' + str(value) + '\n\n', idx = index)
    if cache_value:
        task.value_cache[value_prompt] = value
    return value

def get_values(task, ys, n_evaluate_sample, evaluator_method, cache_value=True):
    values = []
    local_value_cache = {}
    for y in ys:  # each partial output
        print(y)
        if y in local_value_cache:  # avoid duplicate candidates
            value = 0
        else:    
            value = get_value(task, y, n_evaluate_sample, evaluator_method, cache_value=cache_value)
            local_value_cache[y] = value
        values.append(value)
    return values


def evaluation(args, task, idx, graph):
    global index
    index = idx
    for _, node in graph.nodes.items():
        # evaluator
        start_time = time.time()
        # skip root node
        if node['answer'] == None:
            continue
        y = [node['answer']]
        values = get_values(task, y, args.n_evaluate_sample, args.evaluator_method)
        node['value'] = values[0]
        end_time = time.time()
        evaluation_time = end_time - start_time
        node['evaluation cost time'] = evaluation_time
        node['ancestor_distance'] = task.distance_calculator(graph.nodes[str(node['parent_node'])]['value'], graph.nodes[str(node['parent_node'])]['ancestor_distance'], args.n_evaluate_sample, args.evaluator_method)
    graph.show_in_nodes()