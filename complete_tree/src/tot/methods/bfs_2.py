import itertools
import numpy as np
from functools import partial
from tot.models import gpt
import tot.record_functions as record
import tot.tasks.tree_graph as tree_graph
import tot.tasks.draw as draw
import tot.methods.evaluator as evaluator
import re
import time

index = 0 # idx


def bfs(args, task, idx, graph, to_print=True):
    global gpt, index
    index = idx
    cost_time = 0
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    x = task.get_input(idx)  # input
    ys = [(task.get_id() if task.id == 0 else 0, '', 0)]  # current output candidates
    infos = []

    print('-----bfs-----')
    record.Record_txt(record.record_file_name, '\n-----bfs-----\n', idx)
    for step in range(task.steps - 1):
        tuple_ys = []
        for y in ys:
            new_list, _, child_nodes_cost_time = graph.child_to_list(y[0])
            tuple_ys += new_list
            cost_time += sum(child_nodes_cost_time)
            record.Record_txt(record.record_file_name, '\nparent: ' + str(y[0]) + '\ncost time: ' + str(sum(child_nodes_cost_time)) + '\n\n', idx)        

        print(tuple_ys)
        # selection
        selected_ys = sorted(tuple_ys, key=lambda x: x[2], reverse = True)[:args.n_select_sample]
        print(selected_ys)
        record.Record_txt(record.record_file_name, '\nselected nodes:\n' + '\n'.join(list(map(str, selected_ys.copy()))) + '\n' + '\n\n', idx)

        infos.append({'step': step, 'ys': tuple_ys, 'select_new_ys': selected_ys})
        ys = selected_ys
    
    # final generation
    start_time = time.time()
    new_ys = [evaluator.last_step_proposals(task, x, ys[0][1], args.k)]
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    record.Record_txt(record.record_file_name, '\nfinal proposals: ' + str(len(new_ys)) + '\n' + '\n'.join(list(map(str, new_ys.copy()))) + '\n' + '\n\n', idx)
    new_ys = list(itertools.chain(*new_ys))
    ids = list(range(len(new_ys)))
    values = evaluator.last_step_values(task, x, new_ys, args.n_evaluate_sample, args.evaluator_method)
    record.Record_txt(record.record_file_name, '\nfinal evaluation: ' + str(values) + '\n\n', idx)
    top_id = sorted(ids, key=lambda x: values[x], reverse=True)[0]
    answer = new_ys[top_id]
    end_time = time.time()
    cost_time += end_time - start_time
    record.Record_txt(record.record_file_name, '\nfinal generation\nparent: ' + str(ys[0][0]) + '\ncost time' + str(end_time - start_time) + '\n\n', idx)
    final_node = {'id': task.get_id(), 'answer': answer, 'value': values[top_id], 'parent_node': ys[0][0], 'ancestor_distance': 0, 'generation cost time': 0, 'evaluation cost time': 0}
    graph.add_nodes([final_node])
    print('-----end bfs-----')
    record.Record_txt(record.record_file_name, '\n-----end bfs-----\n', idx)

    if to_print: 
        print(infos)
    path = {ys[0][0]}
    draw.bfs_Draw(task, args, infos, graph, idx, path)
    # count traversal nodes
    traversal_nodes = 0
    for step in infos:
        traversal_nodes += len(step['ys'])
    return [answer], {'steps': infos}, traversal_nodes, cost_time