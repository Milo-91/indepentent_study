import itertools
import numpy as np
from functools import partial
from tot.models import gpt
import tot.record_functions as record
import tot.tasks.tree_graph as tree_graph
import tot.tasks.draw as draw
import re
import time

index = 0 # idx

def get_value(task, x, y, n_evaluate_sample, evaluator_method, cache_value=True):
    value_prompt = task.last_value_prompt_wrap(x, y)
    record.Record_txt(record.record_file_name, '\nlast value prompt:\n' + value_prompt + '\n\n', idx = index)
    if 'wrong answer' in y:
        print('we encounter wrong answer')
        return 0
    if cache_value and value_prompt in task.value_cache:
        # record.Record_txt(record.record_file_name, '\n' + value_prompt + '\nuse cache\n\n', idx = index)
        return task.value_cache[value_prompt]
    value_outputs = gpt(value_prompt, n=n_evaluate_sample, stop=None, idx = index, logprobs = False)
    value = task.value_outputs_unwrap(y, value_outputs, )
    record.Record_txt(record.debug_file_name, 'final value: ' + str(value) + '\n\n', idx = index)
    if cache_value:
        task.value_cache[value_prompt] = value
    return value

def get_values(task, x, ys, n_evaluate_sample, evaluator_method, cache_value=True):
    values = []
    local_value_cache = {}
    for y in ys:  # each partial output
        print(y)
        if y in local_value_cache:  # avoid duplicate candidates
            value = 0
        else:    
            value = get_value(task, x, y, n_evaluate_sample, evaluator_method, cache_value=cache_value)
            local_value_cache[y] = value
        values.append(value)
    return values

def last_step_proposals(task, x, y, k):
    global index, gpt
    propose_prompt = task.propose_prompt_wrap(x, y, k)
    proposals = gpt(propose_prompt, n=1, stop=None, idx = index)[0].split('\n')
    
    return [y + _ + '\n' for _ in proposals]

def bfs(args, task, idx, graph, to_print=True):
    global gpt, index
    index = idx
    cost_time = 0
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    x = task.get_input(idx)  # input
    ys = [(task.get_id() if task.id == 0 else 0, '', 0)]  # current output candidates
    infos = []
    distance_list = [0]

    print('-----bfs-----')
    record.Record_txt(record.record_file_name, '\n-----bfs-----\n', idx)
    for step in range(task.steps - 1):
        tuple_ys = []
        for y in ys:
            new_list, distance, parent_cost_time = graph.child_to_list(y[0])
            tuple_ys += new_list
            distance_list.extend(distance)
            cost_time += parent_cost_time
            record.Record_txt(record.record_file_name, '\nparent: ' + str(y[0]) + '\nparent cost time' + str(parent_cost_time) + '\n\n', idx)        

        print(tuple_ys)
        # selection
        selected_ys = sorted(tuple_ys, key=lambda x: x[2], reverse = True)[:args.n_select_sample]
        print(selected_ys)
        record.Record_txt(record.record_file_name, '\nselected nodes:\n' + '\n'.join(list(map(str, selected_ys.copy()))) + '\n' + '\n\n', idx)

        infos.append({'step': step, 'ys': tuple_ys, 'select_new_ys': selected_ys})
        ys = selected_ys
    
    graph.show_in_linked_list()
    graph.show_in_nodes()
    
    # final generation
    start_time = time.time()
    new_ys = [last_step_proposals(task, x, ys[0][1], args.k)]
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    new_ys = list(itertools.chain(*new_ys))
    ids = list(range(len(new_ys)))
    values = get_values(task, x, new_ys, args.n_evaluate_sample)
    top_id = sorted(ids, key=lambda x: values[x], reverse=True)[0]
    answer = new_ys[top_id]
    end_time = time.time()
    cost_time += end_time - start_time
    record.Record_txt(record.record_file_name, '\nparent: ' + str(ys[0][0]) + '\nparent cost time' + str(end_time - start_time) + '\n\n', idx)

    if to_print: 
        print(infos)
    path = {ys[0][0]}
    draw.bfs_Draw(task, args, infos, graph, idx, path)
    # count traversal nodes
    traversal_nodes = 0
    for step in infos:
        traversal_nodes += len(step['ys'])
    return [answer], {'steps': infos}, traversal_nodes, cost_time, reduced_time