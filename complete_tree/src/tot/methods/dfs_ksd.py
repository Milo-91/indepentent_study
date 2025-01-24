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

def add_level_nodes(level_nodes, new_nodes, traversal_nodes):
    for node in new_nodes:
        in_level_nodes = 0
        for level_node in level_nodes:
            if node[0] == level_node[0]:
                in_level_nodes = 1
                break
        if in_level_nodes == 0:
            level_nodes.append(node)
            traversal_nodes += 1
    
    return traversal_nodes

def ksd(args, task, idx, to_print=True, graph=None):
    global gpt, index
    index = idx
    x = task.get_input(idx)  # input
    d_thres = 10000 # a large number
    best_ans = ''
    best_id = 0
    cost_time = 0
    level_nodes = [[] for _ in range(task.steps)]
    infos = []
    if graph == None:
        graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = idx)
    traversal_nodes = 0
    record.Record_txt(record.record_file_name, '\n-----dfs+ksd-----\n', idx)

    # x: question, y: (id, ans, value)
    for b in range(args.n_select_sample):
        gpt = partial(gpt, model=args.backend, temperature=args.temperature)
        print(gpt)
        y = (task.get_id() if task.id == 0 else 0, '', 0) # current output candidates
        distance = 0
        all_traversal = 0
        for step in range(task.steps - 1):
            if all_traversal == 0: # avoid all traversal level before attaching b limit
                is_prune = 0
                record.Record_txt(record.record_file_name, '\ndistance: ' + str(distance) + ', d_thres: ' + str(d_thres) + '\n\n', idx = idx)
                record.Record_txt(record.record_file_name, '\nlevel_nodes\n' + '\n'.join(list(map(str, level_nodes.copy()))), idx)
                record.Record_txt(record.record_file_name, '\nvisited\n' + str(graph.visited), idx)
                print(y[0])
                graph.visit_nodes([{'id': y[0]}])
                # prune
                if distance >= d_thres:
                    record.Record_txt(record.record_file_name, '\n(prune)distance: ' + str(distance) + ', d_thres: ' + str(d_thres) + '\n\n', idx = idx)
                    infos.append({'step': step, 'select_id': y[0], 'select_new_ys': y[1], 'values': y[2], 'is_best': False, 'is_back': True})
                    is_prune = 1

                # if prune this node, then no expand but still find best node in this level
                if is_prune == 0:
                    # Graph
                    parent = y[0]
                    child_list, distance_list, child_cost_time = graph.child_to_list(y[0])
                    temp_node_list = [(*child, distance) for child, distance in zip(child_list, distance_list)]
                    cost_time += sum(child_cost_time)
                    record.Record_txt(record.record_file_name, '\nparent: ' + str(y[0]) + '\nparent cost time' + str(sum(child_cost_time)) + '\n\n', idx)
                    
                    # Put outputs into level_nodes
                    print(child_list)
                    if temp_node_list:
                        traversal_nodes = add_level_nodes(level_nodes[step], temp_node_list.copy(), traversal_nodes)
                        print(parent)
                        level_nodes[step] = sorted(level_nodes[step], key = lambda x: task.distance_calculator(x[2], x[3], args.n_evaluate_sample, args.evaluator_method))
                        record.Record_txt(record.record_file_name, '\nancestor distance:\n' + str([x[3] for x in level_nodes[step]]) + '\n\n', idx = idx)
                        record.Record_txt(record.record_file_name, '\nlevel_nodes distance:\n' + str([task.distance_calculator(x[2], x[3], args.n_evaluate_sample, args.evaluator_method) for x in level_nodes[step]]) + '\n\n', idx = idx)
                
            # selection
            count = 0
            all_traversal = 0
            while graph.visited[level_nodes[step][count][0]] == 1:
                count += 1
                if count == len(level_nodes[step]):
                    all_traversal = 1
                    break
            if all_traversal:
                continue

            select_new_ys = [level_nodes[step][count]]
            distance = task.distance_calculator(select_new_ys[0][2], select_new_ys[0][3], args.n_evaluate_sample, args.evaluator_method)

            print(select_new_ys)
            record.Record_txt(record.record_file_name, '\nselected nodes:\n' + '\n'.join(list(map(str, select_new_ys.copy()))) + '\nnode: ' + str(graph.nodes[select_new_ys[0][0]]) + '\n\n', idx)
            
            y = select_new_ys[0]
            infos.append({'step': step, 'select_id': y[0], 'select_new_ys': y[1], 'values': y[2], 'is_best': True, 'is_back': False})
                
        graph.visit_nodes([{'id': y[0]}])
        # Final Generator
        if is_prune == 1:
            continue
        start_time = time.time()
        new_ys = [get_proposals(task, x, y[1], args.k)]
        new_ys = list(itertools.chain(*new_ys))
        ids = list(range(len(new_ys)))
        values = get_values(task, x, new_ys, args.n_evaluate_sample)
        top_id = sorted(ids, key=lambda x: values[x], reverse=True)[0]
        answer= new_ys[top_id]
        answer_value = values[top_id]
        distance = task.distance_calculator(answer_value, distance, args.n_evaluate_sample)
        end_time = time.time()
        cost_time += end_time - start_time
        record.Record_txt(record.record_file_name, '\nparent: ' + str(y[0]) + '\nparent cost time' + str(end_time - start_time) + '\n\n', idx)
        record.Record_txt(record.record_file_name, '\nanswer: ' + str(answer) + '\n\n', idx = idx)
        # save result and then back
        if distance < d_thres:
            print('max')
            best_ans = answer
            best_id = y[0]
            # dfs with sphere decoding
            d_thres = distance
            record.Record_txt(record.record_file_name, '\nchange best answer\nbest_ans: ' + str(best_ans) + '\nd_thres: ' + str(d_thres) + '\n\n', idx = idx)
        infos.append({'step': step, 'select_id': y[0], 'select_new_ys': answer, 'values': values, 'is_best': True, 'is_back': False})

    graph.show_in_linked_list()
    graph.show_in_nodes()

    parent_id = best_id
    best_path = set()
    while parent_id != 0:
        print(parent_id)
        best_path.add(parent_id)
        parent_id = graph.nodes[parent_id]['parent_node']
    
    print(best_path)
    record.Record_txt(record.record_file_name, '\nbest_path: ' + str(best_path) + '\n\n', idx = idx)

    if to_print:
        print(infos)
    draw.dfs_Draw(task, args, infos, graph, idx, best_path, file_name = 'ksd')
    return [best_ans], {'steps': infos}, traversal_nodes, cost_time