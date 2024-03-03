import itertools
import numpy as np
from functools import partial
from tot.models import gpt
import tot.record_functions as record
import tot.tasks.tree_graph as tree_graph
import tot.tasks.draw as draw

d_thres = 10000
best_ans = ''
best_path = set()
path = set()
infos = []
index = 0 # idx

def get_value(task, x, y, n_evaluate_sample, cache_value=True):
    value_prompt = task.value_prompt_wrap(x, y)
    record.Record_txt(record.record_file_name, '\nvalue prompt: ' + value_prompt + '\n\n', idx = index)
    if cache_value and value_prompt in task.value_cache:
        return task.value_cache[value_prompt]
    value_outputs = gpt(value_prompt, n=n_evaluate_sample, stop=None, idx = index)
    value = task.value_outputs_unwrap(x, y, value_outputs)
    if cache_value:
        task.value_cache[value_prompt] = value
    return value

def get_values(task, x, ys, n_evaluate_sample, cache_value=True):
    values = []
    local_value_cache = {}
    for y in ys:  # each partial output
        if y in local_value_cache:  # avoid duplicate candidates
            value = 0
        else:    
            value = get_value(task, x, y, n_evaluate_sample, cache_value=cache_value)
            local_value_cache[y] = value
        values.append(value)
    return values

def get_proposals(task, x, y, k):
    global index
    propose_prompt = task.propose_prompt_wrap(x, y, k)
    record.Record_txt(record.record_file_name, '\npropose prompt: ' + propose_prompt + '\n\n', idx = index)
    proposals = gpt(propose_prompt, n=1, stop=None, idx = index)[0].split('\n')
    return [y + _ + '\n' for _ in proposals]

# x: question, y: (id, ans, value)
def __dfs__(args, task, idx, x, y, graph, distance, t, to_print = True, sd = False, greedy = False):
    global best_ans, best_path, path, d_thres, infos
    record.Record_txt(record.record_file_name, f'\n----------step {t}----------\n\n', idx = idx)
    record.Record_txt(record.record_file_name, '\ndistance: ' + str(distance) + '\n\n', idx = idx)
    # if achieving leaf node
    if t == task.steps - 1:
        # final generation
        new_ys = [get_proposals(task, x, y[1], args.k)]
        new_ys = list(itertools.chain(*new_ys))
        ids = list(range(len(new_ys)))
        values = get_values(task, x, new_ys, args.n_evaluate_sample)
        top_id = sorted(ids, key=lambda x: values[x], reverse=True)[0]
        answer= new_ys[top_id]
        record.Record_txt(record.record_file_name, '\nanswer: ' + str(answer) + '\n\n', idx = idx)
        # save result and then back
        is_best = False
        if distance < d_thres:
            print('max')
            best_ans = answer
            best_path = path.copy()
            is_best = True
            # dfs with sphere decoding
            d_thres = distance
            record.Record_txt(record.record_file_name, '\nchange best answer\nbest_ans: ' + str(best_ans) + '\nd_thres: ' + str(d_thres) + '\n\n', idx = idx)
        infos.append({'step': t, 'select_id': y[0], 'select_new_ys': answer, 'values': values, 'is_best': is_best, 'is_back': False})
        
        return

    # Graph
    parent = y[0]
    graph.add_head_list_len(parent)
    # if has not visited yet
    if graph.tree_head[parent]['next_node']['node'] == None:
        # Generator
        new_ys = [get_proposals(task, x, y[1], args.k)]
        new_ys = list(itertools.chain(*new_ys))
        ids = [task.get_id() for _ in range(len(new_ys))]
        # Evaluator
        values = get_values(task, x, new_ys, args.n_evaluate_sample)

        new_ys = list(zip(ids, new_ys, values))
        new_nodes = list()
        for i in range(len(new_ys)):
            node = {'id': new_ys[i][0], 'answer': new_ys[i][1], 'value': new_ys[i][2], 'parent_node': parent, 'ancestor_distance': distance}
            new_nodes.append(node)
        graph.add_nodes(new_nodes)
    
    # use graph to traversal
    if greedy:
        select_id = np.argmax([x[2] for x in new_ys])
        next_y = new_ys[select_id]
        distance = task.distance_calculator(next_y[2], distance, args.n_evaluate_sample)
        __dfs__(args, task, idx, x, next_y, graph, distance, t + 1, to_print = True, sd = sd, greedy = True)
    else:
        input = graph.tree_head[parent]['next_node']
        while input['node'] != None:
            input_node = input['node']
            # if distance > d_thres -> prune
            origin_distance = distance
            print(input_node['value'], distance, args.n_evaluate_sample)
            distance = task.distance_calculator(input_node['value'], distance, args.n_evaluate_sample)
            record.Record_txt(record.record_file_name, '\ndistance: ' + str(distance) + '\nd_thres: ' + str(d_thres) + '\n', idx = idx)
            if distance < d_thres:    
                # put input_node into next step
                record.Record_txt(record.record_file_name, '\nselected node: ' + str(input_node) + '\n\n', idx = idx)
                infos.append({'step': t, 'select_id': input_node['id'], 'select_new_ys': input_node['answer'], 'values': values, 'is_best': False, 'is_back': False})
                print(f'distance: {distance}')
                path.add(input_node['id'])
                __dfs__(args, task, idx, x, (input_node['id'], input_node['answer'], input_node['value']), graph, distance, t + 1, to_print = True, sd = sd)
                path.remove(input_node['id'])
            else:
                infos.append({'step': t, 'select_id': input_node['id'], 'select_new_ys': input_node['answer'], 'values': values, 'is_best': False, 'is_back': True})
                record.Record_txt(record.record_file_name, '\n(prune)selected node: ' + str(input_node) + '\n\n', idx = idx)

            # reset distance
            distance = origin_distance
            input = input['next_node']
    
    return

def dfs(args, task, idx, to_print = True, sd = False):
    global d_thres, gpt, best_ans, best_path, path, infos, index
    # reset global variables
    index = idx
    d_thres = 10000
    best_ans = ''
    best_path = set()
    path = set()
    infos = []
    # initialize
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    x = task.get_input(idx)  # input
    y = (task.get_id(), '', 0)  # current output candidates (id, answer, value)
    
    graph = tree_graph.graph(k = args.k, idx = idx)
    
    # Greedy to define d_thres
    # best_node, max_value = Greedy(llm, node, graph)
    print(f'd_thres: {d_thres}')
    __dfs__(args, task, idx, x, y, graph, distance = 0, t = 0, to_print = to_print, sd = sd)
    print(f'd_thres: {d_thres}')
    print(best_ans)
    record.Record_txt(record.record_file_name, '\nbest node: ' + str(best_ans) + '\nd_thres: ' + str(d_thres) + '\n\n', idx = idx)
    
    graph.show_in_linked_list()
    graph.show_in_nodes()

    if to_print:
        print(infos)
    draw.dfs_Draw(task, args, infos, graph, idx, best_path)
    return [best_ans], {'steps': infos}, task.id