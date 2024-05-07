import itertools
import numpy as np
from functools import partial
from tot.models import gpt
import tot.record_functions as record
import tot.tasks.tree_graph as tree_graph
import tot.tasks.draw as draw
import re

d_thres = 10000 # a large number
best_ans = ''
best_path = set()
path = set()
infos = []
index = 0 # idx
traversal_nodes = 0
max_steps = 0

def get_value(task, x, y, n_evaluate_sample, cache_value=True):
    value_prompt = task.value_prompt_wrap(x, y)
    # record.Record_txt(record.record_file_name, '\nvalue prompt: ' + value_prompt + '\n\n', idx = index)
    if 'wrong answer' in y:
        return 0
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
    global index, gpt
    propose_prompt = task.propose_prompt_wrap(x, y, k)
    if 'Answer' in propose_prompt:
        gpt = partial(gpt, model='gpt-4')
    # record.Record_txt(record.debug_file_name, '\npropose prompt: ' + propose_prompt + '\n\n', idx = index)
    proposals = gpt(propose_prompt, n=1, stop=None, idx = index)[0].split('\n')
    # add left
    for i in range(len(proposals)):
        if 'answer' in proposals[i].lower():
            continue
        # record.Record_txt(record.record_file_name, '\nget current numbers: ' + get_current_numbers(y if y else x) + '\n\n', idx = index)
        proposals[i] = add_left(proposals[i], get_current_numbers(y if y else x))
    return [y + _ + '\n' for _ in proposals]

def add_left(response, input_string):
    pattern = r"(-?[0-9\.]+)[\s]*([\+\-\*\/])[\s]*(-?[0-9\.]+)[\s]*=[\s]*(-?[0-9\.]+)[\s]*"
    match = re.match(pattern, response)
    if match:
        print(match.group(1), match.group(3), match.group(4))
        x1 = ' ' + match.group(1) + ' '
        x2 = ' ' + match.group(3) + ' '
        y = ' ' + match.group(4) + ' '
        check = re.search(re.compile(x1), input_string)
        x1_fount = 0
        x2_fount = 0
        if check:
            input_string = input_string.replace(x1, ' ', 1)
            # print('x1 found')
            x1_fount = 1
        check = re.search(re.compile(x2), input_string)
        if check:
            input_string = input_string.replace(x2, y, 1)
            # print('x2 found')
            x2_fount = 1
        input_string = input_string.strip()
        input_string = input_string.replace('  ', ' ')
        print(input_string)
        if x1_fount and x2_fount:
            response = response + f' ( left: {input_string} )'
        else:
            response = 'wrong answer'
    else:
        print('wrong format')
        response = 'wrong answer'

    return response

def get_current_numbers(y: str) -> str:
    last_line = y.strip().split('\n')[-1]
    return ' ' + last_line.split('left: ')[-1].split(')')[0].strip() + ' '

# x: question, y: (id, ans, value)
def __dfs__(args, task, idx, x, y, graph, distance, t, to_print = True, sd = False, greedy = False, sorting = False, high_acc_mode = False):
    global best_ans, best_path, path, d_thres, infos, gpt, traversal_nodes
    record.Record_txt(record.record_file_name, f'\n----------step {t}----------\n\n', idx = idx)
    record.Record_txt(record.record_file_name, '\ndistance: ' + str(distance) + '\n\n', idx = idx)
    # if achieving leaf node
    if t == task.steps - 1:
        # final generation
        new_ys = [get_proposals(task, x, y[1], args.k)]
        gpt = partial(gpt, model=args.backend, temperature=args.temperature)
        new_ys = list(itertools.chain(*new_ys))
        ids = list(range(len(new_ys)))
        values = get_values(task, x, new_ys, args.n_evaluate_sample)
        top_id = sorted(ids, key=lambda x: values[x], reverse=True)[0]
        answer= new_ys[top_id]
        answer_value = values[top_id]
        record.Record_txt(record.record_file_name, '\nanswer: ' + str(answer) + '\n\n', idx = idx)
        distance = task.distance_calculator(answer_value, distance, args.n_evaluate_sample)
        # save result and then back
        is_best = False
        if distance < d_thres:
            print('max')
            if high_acc_mode:
                acc = task.test_output(idx = idx, output = answer)
                if acc['r'] == 1:
                    best_ans = answer
                    best_path = path.copy()
            else:
                best_ans = answer
                best_path = path.copy()
            is_best = True
            # dfs with sphere decoding
            d_thres = distance
            record.Record_txt(record.record_file_name, '\nchange best answer\nbest_ans: ' + str(best_ans) + '\nd_thres: ' + str(d_thres) + '\n\n', idx = idx)
        infos.append({'step': t, 'select_id': y[0], 'select_new_ys': answer, 'values': answer_value, 'is_best': is_best, 'is_back': False})
        node = {'id': -1 * y[0], 'answer': answer, 'value': answer_value, 'parent_node': y[0], 'ancestor_distance': distance}
        graph.add_nodes([node])
        return

    # Graph
    parent = y[0]
    graph.add_head_list_len(parent)
    # if has not visited yet
    if graph.tree_head[parent]['next_node']['node'] == None:
        # Generator
        record.Record_txt(record.record_file_name, '\n-----Generator-----\n\n', idx)
        new_ys = [get_proposals(task, x, y[1], args.k)]
        new_ys = list(itertools.chain(*new_ys))
        ids = [task.get_id() for _ in range(len(new_ys))]
        record.Record_txt(record.record_file_name, '\nnew_ys after itertools\n' + '\n'.join(list(map(str, new_ys.copy()))), idx)
        record.Record_txt(record.record_file_name, '\n-----end Generator-----\n\n', idx)
        # Evaluator
        record.Record_txt(record.record_file_name, '\n-----Evaluator-----\n\n', idx)
        values = get_values(task, x, new_ys, args.n_evaluate_sample)
        record.Record_txt(record.record_file_name, '\nvalues:\n' + '\n'.join(list(map(str, values.copy()))) + '\n\n', idx)
        record.Record_txt(record.record_file_name, '\n-----end Evaluator-----\n\n', idx)
        
        new_ys = list(zip(ids, new_ys, values))
        # Sort
        if sorting:
            new_ys = sorted(new_ys, key  = lambda x: x[2], reverse = True)

        new_nodes = list()
        for i in range(len(new_ys)):
            node = {'id': new_ys[i][0], 'answer': new_ys[i][1], 'value': new_ys[i][2], 'parent_node': parent, 'ancestor_distance': distance}
            new_nodes.append(node)
        graph.add_nodes(new_nodes)

    # use graph to traversal
    if greedy:
        new_ys, _ = graph.child_to_list(parent)
        select_id = np.argmax([x[2] for x in new_ys])
        next_y = new_ys[select_id]
        distance = task.distance_calculator(next_y[2], distance, args.n_evaluate_sample)
        __dfs__(args, task, idx, x, next_y, graph, distance, t + 1, to_print = True, sd = sd, greedy = True, sorting = sorting, high_acc_mode = high_acc_mode)
    else:
        input = graph.tree_head[parent]['next_node']
        while input['node'] != None:
            traversal_nodes += 1
            input_node = input['node']
            # if distance > d_thres -> prune
            origin_distance = distance
            print(input_node['value'], distance, args.n_evaluate_sample)
            distance = task.distance_calculator(input_node['value'], distance, args.n_evaluate_sample)
            record.Record_txt(record.record_file_name, '\ndistance: ' + str(distance) + '\nd_thres: ' + str(d_thres) + '\n', idx = idx)
            if distance < d_thres:    
                # put input_node into next step
                record.Record_txt(record.record_file_name, '\nselected node: ' + str(input_node) + '\n\n', idx = idx)
                infos.append({'step': t, 'select_id': input_node['id'], 'select_new_ys': input_node['answer'], 'values': input_node['value'], 'is_best': False, 'is_back': False})
                print(f'distance: {distance}')
                path.add(input_node['id'])
                __dfs__(args, task, idx, x, (input_node['id'], input_node['answer'], input_node['value']), graph, distance, t + 1, to_print = True, sd = sd, sorting = sorting, high_acc_mode = high_acc_mode)
                path.remove(input_node['id'])
            else:
                infos.append({'step': t, 'select_id': input_node['id'], 'select_new_ys': input_node['answer'], 'values': input_node['value'], 'is_best': False, 'is_back': True})
                record.Record_txt(record.record_file_name, '\n(prune)selected node: ' + str(input_node) + '\n\n', idx = idx)

            # reset distance
            distance = origin_distance
            input = input['next_node']
    
    return

# sd, greedy flag not using
def dfs(args, task, idx, to_print = True, sd = False, sorting = False, high_acc_mode = False, graph = None):
    global d_thres, gpt, best_ans, best_path, path, infos, index, traversal_nodes, max_steps
    # reset global variables
    index = idx
    d_thres = 10000 # a large number
    best_ans = ''
    best_path = set()
    path = set()
    infos = []
    traversal_nodes = 0
    max_steps = 2 * (args.n_select_sample + 1) * args.k
    # initialize
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    x = task.get_input(idx)  # input
    y = (task.get_id() if task.id == 0 else 0, '', 0)  # current output candidates (id, answer, value)
    
    if graph == None:
        graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = idx)
    
    # Greedy to define d_thres
    # best_node, max_value = Greedy(llm, node, graph)
    print(f'd_thres: {d_thres}')
    __dfs__(args, task, idx, x, y, graph, distance = 0, t = 0, to_print = to_print, sd = sd, sorting = sorting, high_acc_mode = high_acc_mode)
    print(f'd_thres: {d_thres}')
    print(best_ans)
    record.Record_txt(record.record_file_name, '\nbest node: ' + str(best_ans) + '\nd_thres: ' + str(d_thres) + '\n\n', idx = idx)
    
    graph.show_in_linked_list()
    graph.show_in_nodes()

    if to_print:
        print(infos)
    draw.dfs_Draw(task, args, infos, graph, idx, best_path)
    return [best_ans], {'steps': infos}, traversal_nodes