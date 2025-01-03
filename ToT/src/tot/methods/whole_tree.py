import itertools
import numpy as np
from functools import partial
from tot.models import gpt
import tot.record_functions as record
import tot.tasks.tree_graph as tree_graph
import tot.tasks.draw as draw
import re
import time
import sympy

index = 0 # idx
associative_cache = []

def get_value(task, x, y, n_evaluate_sample, cache_value=True):
    value_prompt = task.value_prompt_wrap(x, y)
    # record.Record_txt(record.record_file_name, '\nvalue prompt: ' + value_prompt + '\n\n', idx = index)
    if 'wrong answer' in y:
        return 0
    if cache_value and value_prompt in task.value_cache:
        # record.Record_txt(record.record_file_name, '\n' + value_prompt + '\nuse cache\n\n', idx = index)
        return task.value_cache[value_prompt]
    value_outputs, avg_probs = gpt(value_prompt, n=n_evaluate_sample, stop=None, idx = index)
    print(avg_probs)
    record.Record_txt(record.debug_file_name, '\nvalue outputs: ' + str(value_outputs) + '\navg probs: ' + str(avg_probs) + '\n\n', idx = index)
    value = task.value_outputs_unwrap(x, y, value_outputs, avg_probs)
    record.Record_txt(record.debug_file_name, 'final value: ' + str(value) + '\n\n', idx = index)
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

def get_proposals(task, x, y, k, cache_propose = False):
    global index, gpt
    propose_prompt = task.propose_prompt_wrap(x, y, k)
    if cache_propose and propose_prompt in task.propose_cache:
        record.Record_txt(record.record_file_name, '\n' + propose_prompt + '\nuse cache\n\n' + task.propose_cache[propose_prompt] + '\n', idx = index)
        return task.propose_cache[propose_prompt], True
    # record.Record_txt(record.debug_file_name, '\npropose prompt: ' + propose_prompt + '\n\n', idx = index)
    
    # Final Generator use Gpt-4
    if 'Answer' in propose_prompt:
        gpt = partial(gpt, model='gpt-4')
    proposals, _ = gpt(propose_prompt, n=1, stop=None, idx = index)
    proposals = proposals[0].split('\n')
    # state filter
    proposals = state_filter(proposals)
    # add left
    for i in range(len(proposals)):
        if 'answer' in proposals[i].lower():
            continue
        # record.Record_txt(record.record_file_name, '\nget current numbers: ' + get_current_numbers(y if y else x) + '\n\n', idx = index)
        proposals[i] = add_left(proposals[i], get_current_numbers(y if y else x))
    proposals = list(filter(lambda x: x != 'wrong answer', proposals))
    task.propose_cache[propose_prompt] = [y + _ + '\n' for _ in proposals]
    # record.Record_txt(record.debug_file_name, '\npropose prompt: ' + propose_prompt + '\n\n', idx = index)
    return [y + _ + '\n' for _ in proposals], False

def Associative_filter(x, y):
    x_copy = x
    left = None
    x_left = '( left: ' + x + ' )'
    print(x_left)
    path = list(filter(None, y.split('\n')))[::-1]
    path.append(x_left)
    print(path)
    # use '\n' to judge layer of y
    for i in range(y.count('\n')):
        match = re.search(r'(.+)[\s]*=[\s]*(-?[\d.]+)[\s]*\( left:(.+)\)', path[i])
        if match:
            x = ' ( ' + match.group(1).strip() + ' ) ' # not replace ' ' to '' (negative numbers problem)
            y = match.group(2)
            y = ' ' + y + ' '
            print(x, y)
            if left == None:
                left = match.group(3)
                delete_element = list(re.findall(r'-?[\d.]+', left.replace(y, ' ', 1)))
                print('delete element: ' + str(delete_element))
                for element in delete_element:
                    left = left.replace(' ' + element + ' ', ' ', 1)
        else:
            print("cant match path format")
            return None

        left = left.replace(y, x, 1)
        
    print(left)
    # for algebra
    expr = number_to_algebra(x_copy, left)
    return expr

def number_to_algebra(x, path):
    x_set = sorted(list(set(re.findall(r'-?\d+', x))), key = lambda x: int(x)) # sort to avoid number to replace algebra subscript
    x_dict = {}
    for i in range(len(x_set)):
        x_dict.update({x_set[i]: f'x{int(x_set[0]) + i}'}) # x_set[0] + i to avoid number to replace algebra subscript
    print(x_dict)
    for element in x_dict:
        path = path.replace(' ' + element + ' ', ' ' + x_dict[element] + ' ')
    print(path)
    return path

def state_filter(input):
    cache = []
    proposals = []
    for item in input:
        if 'answer' in item.lower():
            continue
        pattern = r"(-?[0-9\.]+)[\s]*([\+\-\*\/])[\s]*(-?[0-9\.]+)[\s]*=[\s]*(-?[0-9\.]+)[\s]*"
        match = re.match(pattern, item)
        if match:
            if match.group(2) == '+' or match.group(2) == '*':
                if f'{match.group(1)} {match.group(2)} {match.group(3)}' not in cache and f'{match.group(3)} {match.group(2)} {match.group(1)}' not in cache:
                    cache.append(f'{match.group(1)} {match.group(2)} {match.group(3)}')
                    proposals.append(item)
                else:
                    record.Record_txt(record.record_file_name, '\nfiltered: ' + str(item) + '\n\n', idx = index)
            else:
                if f'{match.group(1)} {match.group(2)} {match.group(3)}' not in cache:
                    cache.append(f'{match.group(1)} {match.group(2)} {match.group(3)}')
                    proposals.append(item)
                else:
                    record.Record_txt(record.record_file_name, '\nfiltered: ' + str(item) + '\n\n', idx = index)
    record.Record_txt(record.record_file_name, '\ngeneration filter:\n' + '\n'.join(list(map(str, cache.copy()))) + '\n\n', idx = index)
    return proposals
            

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

def build(args, task, idx, graph = None, layers_k=[8, 8, 8]):
    global gpt, index, associative_cache
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    index = idx
    x = task.get_input(idx)  # input
    ys = [(task.get_id(), '', 0)]  # current output candidates
    infos = []
    if graph == None:
        graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = idx)
    root_node = {'id': 0, 'answer': None, 'value': None, 'parent_node': None, 'ancestor_distance': 0, 'cost time': 0}
    graph.add_nodes([root_node])
    distance_list = [0]
    nodes_avg_time_per_layer = [0, 0, 0] # record nodes avg cost time at each layer
    associative_cache = [] # initializing

    for step in range(task.steps - 1):
    # for step in range(1):
        tuple_ys = []
        infos_ys = []
        cost_time_list = []
        generated = 0
        for y in ys:
            parent_id = y[0]
            # if has not visited yet
            if graph.tree_head[y[0]]['next_node']['node'] == None:
                # generator
                start_time = time.time()
                record.Record_txt(record.record_file_name, '\nnode: ' + str(y[0]) + '\n\n', idx = index)
                new_ys, cached = get_proposals(task, x, y[1], layers_k[step])
                # for associative property
                for element in new_ys:
                    remove = 0
                    equation = Associative_filter(x, element)
                    if equation != None:
                        for eq in associative_cache:
                            if sympy.expand(equation) == eq:
                                new_ys.remove(element)
                                remove = 1
                                break
                        if remove == 0:
                            associative_cache.append(sympy.expand(Associative_filter(x, element)))
                record.Record_txt(record.record_file_name, '\nassociative:\n' + '\n'.join(list(map(str, associative_cache.copy()))) + '\ncount: ' + str(len(associative_cache)) + '\n\n', idx = index)
                
                # for proposal cache
                if cached:
                    task.cached_nodes_set.add(parent_id)
                print(new_ys)
                gpt = partial(gpt, model=args.backend, temperature=args.temperature)
                if step == task.steps - 1:
                    ids = list(range(len(new_ys)))
                else:
                    ids = [task.get_id() for _ in range(len(new_ys))]
                
                # evaluator
                values = get_values(task, x, new_ys, args.n_evaluate_sample)
                print(values)
                new_ys = list(zip(ids, new_ys, values))
                new_ys = sorted(new_ys, key  = lambda x: x[0])
                end_time = time.time()
                cost_time_list.append(end_time - start_time)

                record.Record_txt(record.record_file_name, '\n' + str(new_ys) + '\n\n', idx = index)
                tuple_ys += new_ys
                # append to graph
                new_nodes = list()
                for i in range(len(new_ys)):
                    distance = task.distance_calculator(new_ys[i][2], distance_list[y[0]], args.n_evaluate_sample)
                    distance_list.append(distance)
                    node = {'id': new_ys[i][0], 'answer': new_ys[i][1], 'value': new_ys[i][2], 'parent_node': y[0], 'ancestor_distance': distance_list[y[0]], 'cost time': 0}
                    new_nodes.append(node)
                graph.add_head_list_len(task.id)
                print('id: ' + str(task.id))
                new_nodes = sorted(new_nodes, key  = lambda x: task.distance_calculator(x['value'], x['ancestor_distance'], args.n_evaluate_sample))
                graph.add_nodes(new_nodes)
        
                # for json ys
                for element in new_ys:
                    infos_ys.append(element + (parent_id,))
            else:
                generated = 1
                new_list, distance, parent_cost_time = graph.child_to_list(y[0])
                tuple_ys += new_list
                distance_list.extend(distance)
                print("already generated")
                record.Record_txt(record.record_file_name, '\nparent: ' + str(y[0]) + '\nparent cost time' + str(parent_cost_time) + '\n\n', idx)

                # for json ys
                for element in new_list:
                    infos_ys.append(element + (parent_id,))
                    
        nodes_avg_time_per_layer[step] = sum(cost_time_list) / len(cost_time_list)
                    
        # use one variable to detected generated or not (warning: if there are some nodes generated and some are not, there may be an error)
        if generated == 0:
            graph.add_cost_time_in_parent_nodes(ys, cost_time_list)
        # set output as next input
        infos.append({'step': step, 'ys': infos_ys})
        ys = tuple_ys
        

    graph.show_in_linked_list()
    graph.show_in_nodes()
    draw.simple_draw(task, args, graph, idx)
    return 'no answer', {'steps': infos}, task.id, nodes_avg_time_per_layer