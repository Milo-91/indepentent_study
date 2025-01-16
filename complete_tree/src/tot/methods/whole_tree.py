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

def get_proposals(task, x, y, k):
    global index, gpt
    propose_prompt = task.propose_prompt_wrap(x, y, k)
    proposals = gpt(propose_prompt, n=1, stop=None, idx = index)[0].split('\n')
    
    # add left
    for i in range(len(proposals)):
        if 'answer' in proposals[i].lower():
            continue
        # record.Record_txt(record.record_file_name, '\nget current numbers: ' + get_current_numbers(y if y else x) + '\n\n', idx = index)
        proposals[i] = add_left(proposals[i], get_current_numbers(y if y else x))
    proposals = list(filter(lambda x: x != 'wrong answer', proposals))
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

def build(args, task, idx, graph = None):
    global gpt, index
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    print('this is new code')
    index = idx
    x = task.get_input(idx)  # input
    ys = [(task.get_id(), '', 0)]  # current output candidates
    infos = []
    if graph == None:
        graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = idx)
    root_node = {'id': 0, 'answer': None, 'value': None, 'parent_node': None, 'ancestor_distance': 0, 'cost time': 0}
    graph.add_nodes([root_node])

    for step in range(task.steps - 1):
        tuple_ys = []
        infos_ys = []
        for y in ys:
            parent_id = y[0]
            # if has not visited yet
            if graph.tree_head[y[0]]['next_node']['node'] == None:
                # generator
                start_time = time.time()
                record.Record_txt(record.record_file_name, '\nnode: ' + str(y[0]) + '\n' + str(y[1]) + '\n\n', idx = index)
                new_ys = get_proposals(task, x, y[1], k = args.k)
                print(new_ys)
                gpt = partial(gpt, model=args.backend, temperature=args.temperature)
                ids = [task.get_id() for _ in range(len(new_ys))]
                end_time = time.time()
                generation_cost_time = end_time - start_time
                new_ys = list(zip(ids, new_ys))
                
                # evaluator is in another file
                
                record.Record_txt(record.record_file_name, '\n' + str(new_ys) + '\n\n', idx = index)
                tuple_ys += new_ys
                # append to graph
                new_nodes = list()
                for i in range(len(new_ys)):
                    node = {'id': new_ys[i][0], 'answer': new_ys[i][1], 'value': None, 'parent_node': y[0], 'ancestor_distance': None, 'generation cost time': generation_cost_time / len(new_ys)}
                    new_nodes.append(node)
                graph.add_head_list_len(task.id)
        
                # for json ys
                for element in new_ys:
                    infos_ys.append(element + (parent_id,))
            else:
                record.Record_txt(record.debug_file_name, '\nerror in build\n\n', idx = index)
            
        # set output as next input
        infos.append({'step': step, 'ys': infos_ys})
        ys = tuple_ys
        

    graph.show_in_linked_list()
    graph.show_in_nodes()
    draw.simple_draw(task, args, graph, idx)
    return {'steps': infos}, task.id