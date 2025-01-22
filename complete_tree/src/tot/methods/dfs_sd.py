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

d_thres = 10000 # a large number
best_ans = ''
best_path = set()
path = set()
infos = []
index = 0 # idx
traversal_nodes = 0
cost_time = 0


# x: question, y: (id, ans, value)
def __dfs__(args, task, idx, x, y, graph, distance, t, high_acc_mode = False):
    global best_ans, best_path, path, d_thres, infos, gpt, traversal_nodes, cost_time
    record.Record_txt(record.record_file_name, f'\n----------step {t}----------\n\n', idx = idx)
    record.Record_txt(record.record_file_name, '\ndistance: ' + str(distance) + '\n\n', idx = idx)
    # if achieving leaf node
    if t == task.steps - 1:
        # final generation
        start_time = time.time()
        new_ys = [evaluator.last_step_proposals(task, x, y[1], args.k)]
        gpt = partial(gpt, model=args.backend, temperature=args.temperature)
        new_ys = list(itertools.chain(*new_ys))
        ids = list(range(len(new_ys)))
        values = evaluator.last_step_values(task, x, new_ys, args.n_evaluate_sample, args.evaluator_method)
        top_id = sorted(ids, key=lambda x: values[x], reverse=True)[0]
        answer= new_ys[top_id]
        answer_value = values[top_id]
        record.Record_txt(record.record_file_name, '\nanswer: ' + str(answer) + '\n\n', idx = idx)
        distance = task.distance_calculator(answer_value, distance, args.n_evaluate_sample, args.evaluator_method)
        end_time = time.time()
        cost_time += end_time - start_time
        record.Record_txt(record.record_file_name, '\nparent: ' + str(y[0]) + '\ncost time: ' + str(end_time - start_time) + '\n\n', idx)

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
        return

    # Graph
    parent = y[0]
    child_list, distance_list, child_nodes_cost_time = graph.child_to_list(parent)
    cost_time += sum(child_nodes_cost_time)
    record.Record_txt(record.record_file_name, '\nparent: ' + str(parent) + '\nparent cost time' + str(sum(child_nodes_cost_time)) + '\n\n', idx)
    temp_node_list = [(*child, distance) for child, distance in zip(child_list, distance_list)]
    print(temp_node_list)
    child_list = sorted(temp_node_list, key  = lambda x: task.distance_calculator(x[2], x[3], args.n_evaluate_sample, args.evaluator_method))
    for input_node in child_list:
        traversal_nodes += 1
        # if distance > d_thres -> prune
        origin_distance = distance
        print(input_node)
        print(input_node[2], distance, args.n_evaluate_sample)
        distance = task.distance_calculator(input_node[2], distance, args.n_evaluate_sample, args.evaluator_method)
        record.Record_txt(record.record_file_name, '\ndistance: ' + str(distance) + '\nd_thres: ' + str(d_thres) + '\n', idx = idx)
        if distance < d_thres:    
            # put input_node into next step
            record.Record_txt(record.record_file_name, '\nselected node: ' + str(input_node) + '\n\n', idx = idx)
            infos.append({'step': t, 'select_id': input_node[0], 'select_new_ys': input_node[1], 'values': input_node[2], 'is_best': False, 'is_back': False})
            print(f'distance: {distance}')
            path.add(input_node[0])
            __dfs__(args, task, idx, x, input_node, graph, distance, t + 1, high_acc_mode = high_acc_mode)
            path.remove(input_node[0])
        else:
            infos.append({'step': t, 'select_id': input_node[0], 'select_new_ys': input_node[1], 'values': input_node[2], 'is_best': False, 'is_back': True})
            record.Record_txt(record.record_file_name, '\n(prune)selected node: ' + str(input_node) + '\n\n', idx = idx)

        # reset distance
        distance = origin_distance
    
    return

def dfs(args, task, idx, graph, to_print = True,  high_acc_mode = False):
    global d_thres, gpt, best_ans, best_path, path, infos, index, traversal_nodes, cost_time
    # reset global variables
    index = idx
    d_thres = 10000 # a large number
    best_ans = ''
    best_path = set()
    path = set()
    infos = []
    traversal_nodes = 0
    cost_time = 0
    # initialize
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    x = task.get_input(idx)  # input
    y = (task.get_id() if task.id == 0 else 0, '', 0)  # current output candidates (id, answer, value)
    
    
    record.Record_txt(record.record_file_name, '\n-----dfs+sd-----\n', idx)
    # Greedy to define d_thres
    print(f'd_thres: {d_thres}')
    __dfs__(args, task, idx, x, y, graph, distance = 0, t = 0, high_acc_mode = high_acc_mode)
    print(f'd_thres: {d_thres}')
    print(best_ans)
    record.Record_txt(record.record_file_name, '\nbest node: ' + str(best_ans) + '\nd_thres: ' + str(d_thres) + '\n\n', idx = idx)
    

    if to_print:
        print(infos)
    # draw.dfs_Draw(task, args, infos, graph, idx, best_path)
    return [best_ans], {'steps': infos}, traversal_nodes, cost_time