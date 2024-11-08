import os
import json
import argparse
import tot.record_functions as record
import datetime
import time
import copy
import sys
import jsonpickle

from tot.tasks import get_task
from tot.tasks import draw
import tot.tasks.tree_graph as tree_graph
from tot.methods.bfs import solve, naive_solve
from tot.methods.bfs_2 import bfs
from tot.methods.dfs_sd import dfs
from tot.methods.dfs_ksd import ksd
from tot.methods.fsd import fsd
from tot.methods.fsd_2 import fsd_2
from tot.methods.fsd_graph import fsd_graph
from tot.methods.whole_tree import build
from tot.models import gpt_usage

def error_log(type, value, traceback):
    print(f'type: {type}, value: {value}, traceback: {traceback}')
    with open('error.log', 'a') as file:
        file.write(f'type: {type}  value: {value}  traceback: {traceback}\n')

def run(args):
    sys.excepthook = error_log
    task = get_task(args.task)
    logs, cnt_avg, cnt_any = [], 0, 0
    bfs_cnt_avg = 0
    dfs_cnt_avg = 0
    ksd_cnt_avg = 0
    fsd_cnt_avg = 0
    fsd73_cnt_avg = 0
    fsd37_cnt_avg = 0
    total_cost_time = 0
    graph_list = []
    nodes_avg_time_per_layer = [0, 0, 0]
    folder_index = 0
    folder_name = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}/{folder_index}'
    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', indent=4)
    while os.path.exists(folder_name):
        folder_index += 1
        folder_name = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}/{folder_index}'
    os.makedirs(os.path.dirname(folder_name), exist_ok=True)
    record.Init_folder_path(folder_name)
    draw.Init_image_folder_path(folder_name)
    if args.naive_run:
        file = f'./logs/{args.task}/{args.backend}_{args.temperature}_naive_{args.prompt_sample}_sample_{args.n_generate_sample}_start{args.task_start_index}_end{args.task_end_index}.json'
    else:
        file_index = 0
        file = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_{file_index}.json')
        while os.path.exists(file):
            file_index += 1
            file = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_{file_index}.json')
    record.Init_record_file(record.acc_file_name, f'model: {args.backend}\ntemperature: {args.temperature}\nalgorithm: {args.algorithm}\nk: {args.k}\nb: {args.n_select_sample}\nstart_index: {args.task_start_index}\nend_index: {args.task_end_index}\ndate: {datetime.date.today()}\n\n')
    print('start task')
    for i in range(args.task_start_index, args.task_end_index):
        traversal_nodes = 0
        record.Init_record_file(record.record_file_name, f'model: {args.backend}\ntemperature: {args.temperature}\nalgorithm: {args.algorithm}\nk: {args.k}\nb: {args.n_select_sample}\nidx: {i}\ndate: {datetime.date.today()}\n\n', idx = i)
        # record.Init_record_file(record.debug_file_name, '', idx = i)
        # reset id
        task.reset_id()
        # solve
        start_time = time.time()
        if args.algorithm == 'bfs':
            if args.naive_run:
                ys, info = naive_solve(args, task, i) 
            else:
                # ys, info = solve(args, task, i)
                ys, info, bfs_cost_time, bfs_reduced_time = bfs(args, task, i)
        elif args.algorithm == 'dfs+sd':
            ys, info, traversal_nodes, dfs_cost_time, dfs_reduced_time = dfs(args, task, i, sd = True, sorting = True, high_acc_mode = False)
        elif args.algorithm == 'dfs+ksd':
            ys, info, traversal_nodes,  ksd_cost_time, ksd_reduced_time = ksd(args, task, i)
        elif args.algorithm == 'fsd_2':
            ys, info, traversal_nodes, fsd_cost_time, fsd_reduced_time = fsd_2(args, task, i)
        elif args.algorithm == 'fsd_graph':
            graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = i)
            graph.__load_from_json__('graph.json', i - 900)
            graph.show_in_linked_list()
            graph.show_in_nodes()
            ys, info, traversal_nodes, fsd_cost_time, _ = fsd_graph(args, task, i, graph=graph, layer1_b=6, layer2_b=4)
            total_cost_time += fsd_cost_time
        elif args.algorithm == 'no_algorithm':
            ys, info, traversal_nodes, nodes_avg_time_per_layer_temp = build(args, task, i, layers_k = [12, 6, 4])
        elif args.algorithm == 'whole_tree':
            graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = i)
            if args.graph_json == True:
                graph.__load_from_json__('graph.json', i - 900)
                # graph.show_in_linked_list()
                # graph.show_in_nodes()
            task.cached_nodes_set = set()
            ys, info, traversal_nodes, nodes_avg_time_per_layer_temp = build(args, task, i, graph = graph)
            nodes_avg_time_per_layer = [a + b for a, b in zip(nodes_avg_time_per_layer, nodes_avg_time_per_layer_temp)]
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            bfs_ys, bfs_info, bfs_traversal_nodes, bfs_cost_time, bfs_reduced_time = bfs(args, task, i, graph = graph_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            dfs_ys, dfs_info, dfs_traversal_nodes, dfs_cost_time, dfs_reduced_time = dfs(args, task, i, sd = True, sorting = True, high_acc_mode = False, graph = graph_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            ksd_ys, ksd_info, ksd_traversal_nodes, ksd_cost_time, ksd_reduced_time = ksd(args, task, i, graph = graph_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            fsd_ys, fsd_info, fsd_traversal_nodes, fsd_cost_time, fsd_reduced_time = fsd(args, task, i, graph = graph_copy, layer1_b=6, layer2_b=3)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            fsd73_ys, fsd73_info, fsd73_traversal_nodes, fsd73_cost_time, fsd73_reduced_time = fsd(args, task, i, graph=graph_copy, layer1_b=7, layer2_b=1)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            fsd37_ys, fsd37_info, fsd37_traversal_nodes, fsd37_cost_time, fsd37_reduced_time = fsd(args, task, i, graph=graph_copy, layer1_b=8, layer2_b=3)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_list.append({'total_element': graph.total_element, 'tree_head': graph.tree_head.copy(), 'nodes': graph.nodes.copy(), 'visited': graph.visited.copy(), 'idx': graph.idx})
        end_time = time.time()
        print(end_time - start_time)
        total_cost_time += end_time - start_time
        if args.algorithm == 'whole_tree':
            record.Record_txt(record.record_file_name, '\nbfs_ys = ' + str(bfs_ys) + '\ndfs+sd_ys = ' + str(dfs_ys) + '\ndfs+ksd_ys = ' + str(ksd_ys) + '\n\n', idx = i)
        else:
            record.Record_txt(record.record_file_name, '\nys = ' + str(ys) + '\n\n', idx = i)
        record.Record_txt(record.record_file_name, '\n-----task complete-----\n', idx = i)
        # log
        if args.algorithm == 'whole_tree':
            bfs_infos = [task.test_output(i, y) for y in bfs_ys]
            dfs_infos = [task.test_output(i, y) for y in dfs_ys]
            ksd_infos = [task.test_output(i, y) for y in ksd_ys]
            fsd_infos = [task.test_output(i, y) for y in fsd_ys]
            fsd73_infos = [task.test_output(i, y) for y in fsd73_ys]
            fsd37_infos = [task.test_output(i, y) for y in fsd37_ys]
            
            info.update({'idx': i, 'traversal_nodes': traversal_nodes})                                                                                                                                                  # %7 0
            bfs_info.update({'idx': i, 'ys': bfs_ys, 'infos': bfs_infos, 'traversal_nodes': bfs_traversal_nodes, 'cost time': bfs_cost_time, 'reduced time': bfs_reduced_time, 'usage_so_far': gpt_usage(args.backend)}) # %7 1
            dfs_info.update({'idx': i, 'ys': dfs_ys, 'infos': dfs_infos, 'traversal_nodes': dfs_traversal_nodes, 'cost time': dfs_cost_time, 'reduced time': dfs_reduced_time, 'usage_so_far': gpt_usage(args.backend)}) # %7 2
            ksd_info.update({'idx': i, 'ys': ksd_ys, 'infos': ksd_infos, 'traversal_nodes': ksd_traversal_nodes, 'cost time': ksd_cost_time, 'reduced time': ksd_reduced_time, 'usage_so_far': gpt_usage(args.backend)}) # %7 3
            fsd_info.update({'idx': i, 'ys': fsd_ys, 'infos': fsd_infos, 'traversal_nodes': fsd_traversal_nodes, 'cost time': fsd_cost_time, 'reduced time': fsd_reduced_time, 'usage_so_far': gpt_usage(args.backend)}) # %7 4
            fsd73_info.update({'idx': i, 'ys': fsd73_ys, 'infos': fsd73_infos, 'traversal_nodes': fsd73_traversal_nodes, 'cost time': fsd73_cost_time, 'reduced time': fsd73_reduced_time, 'usage_so_far': gpt_usage(args.backend)}) # %7 5
            fsd37_info.update({'idx': i, 'ys': fsd37_ys, 'infos': fsd37_infos, 'traversal_nodes': fsd37_traversal_nodes, 'cost time': fsd37_cost_time, 'reduced time': fsd37_reduced_time, 'usage_so_far': gpt_usage(args.backend)}) # %7 6
            record.Record_txt(record.record_file_name, '\nbfs_ys: ' + str(bfs_ys)  + ', infos: ' + str(bfs_infos) + '\ndfs+sd_ys: ' + str(dfs_ys) + ', infos: ' + str(dfs_infos) + '\ndfs+ksd_ys: ' + str(ksd_ys) + ', infos: ' + str(ksd_infos) + '\nfsd_ys: ' + str(fsd_ys) + ', infos: ' + str(fsd_infos) + '\n\n', idx = i) 
            record.Record_txt(record.record_file_name, '\ncost time: ' + str(end_time - start_time) + '\n\n', idx = i)
            record.Record_txt(record.acc_file_name, str(i) + '\n\b bfs_ys: ' + str(bfs_ys[0])  + ', acc: ' + str(bfs_infos[0]) + ', traversal nodes: ' + str(bfs_traversal_nodes) + ', cost time: ' + str(bfs_cost_time) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+sd_ys: ' + str(dfs_ys[0])  + ', acc: ' + str(dfs_infos[0]) + ', traversal nodes: ' + str(dfs_traversal_nodes) + ', cost time: ' + str(dfs_cost_time) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+ksd_ys: ' + str(ksd_ys[0])  + ', acc: ' + str(ksd_infos[0]) + ', traversal nodes: ' + str(ksd_traversal_nodes) + ', cost time: ' + str(ksd_cost_time) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b fsd_ys (8, 2): ' + str(fsd_ys[0])  + ', acc: ' + str(fsd_infos[0]) + ', traversal nodes: ' + str(fsd_traversal_nodes) + ', cost time: ' + str(fsd_cost_time) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b fsd_ys (7, 3): ' + str(fsd73_ys[0])  + ', acc: ' + str(fsd73_infos[0]) + ', traversal nodes: ' + str(fsd73_traversal_nodes) + ', cost time: ' + str(fsd73_cost_time) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b fsd_ys (3, 7): ' + str(fsd37_ys[0])  + ', acc: ' + str(fsd37_infos[0]) + ', traversal nodes: ' + str(fsd37_traversal_nodes) + ', cost time: ' + str(fsd37_cost_time) + '\n\n')
            record.Record_txt(record.propose_cache_file, 'cached nodes set: ' + str(task.cached_nodes_set) + '\n\n', idx=i)
            record.Record_txt(record.propose_cache_file, 'propose cache:\n' + json.dumps(task.propose_cache, indent=4) + '\n\n', idx=i)
            logs.append(info)
            logs.append(bfs_info)
            logs.append(dfs_info)
            logs.append(ksd_info)
            logs.append(fsd_info)
            logs.append(fsd73_info)
            logs.append(fsd37_info)
            with open(file, 'w') as f:
                json.dump(logs, f, indent=4)
    
            # log main metric
            bfs_accs = [info['r'] for info in bfs_infos]
            dfs_accs = [info['r'] for info in dfs_infos]
            ksd_accs = [info['r'] for info in ksd_infos]
            fsd_accs = [info['r'] for info in fsd_infos]
            fsd37_accs = [info['r'] for info in fsd73_infos]
            fsd73_accs = [info['r'] for info in fsd37_infos]
            bfs_cnt_avg += sum(bfs_accs) / len(bfs_accs)
            print(i, 'bfs: sum(accs)', sum(bfs_accs), 'cnt_avg', bfs_cnt_avg, '\n')
            dfs_cnt_avg += sum(dfs_accs) / len(dfs_accs)
            print(i, 'dfs: sum(accs)', sum(dfs_accs), 'cnt_avg', dfs_cnt_avg, '\n')
            ksd_cnt_avg += sum(ksd_accs) / len(ksd_accs)
            print(i, 'ksd: sum(accs)', sum(ksd_accs), 'cnt_avg', ksd_cnt_avg, '\n')
            fsd_cnt_avg += sum(fsd_accs) / len(fsd_accs)
            print(i, 'fsd: sum(accs)', sum(fsd_accs), 'cnt_avg', fsd_cnt_avg, '\n')
            fsd73_cnt_avg += sum(fsd73_accs) / len(fsd73_accs)
            print(i, 'fsd (7, 3): sum(accs)', sum(fsd73_accs), 'cnt_avg', fsd73_cnt_avg, '\n')
            fsd37_cnt_avg += sum(fsd37_accs) / len(fsd37_accs)
            print(i, 'fsd (3, 7): sum(accs)', sum(fsd37_accs), 'cnt_avg', fsd37_cnt_avg, '\n')
        else:
            infos = [task.test_output(i, y) for y in ys]
            info.update({'idx': i, 'x': task.get_input(i), 'ys': ys, 'infos': infos, 'traversal_nodes': traversal_nodes, 'usage_so_far': gpt_usage(args.backend)})
            record.Record_txt(record.record_file_name, '\nys: ' + str(ys) + '\ninfos: ' + str(infos) + '\n\n', idx = i)
            record.Record_txt(record.record_file_name, '\ncost time: ' + str(end_time - start_time) + '\n\n', idx = i)
            record.Record_txt(record.acc_file_name, str(i) + ': ys: ' + str(ys[0]) + ', acc: ' + str(infos[0]) + ', traversal nodes: ' + str(traversal_nodes) + '\n\n')
            logs.append(info)
            with open(file, 'w') as f:
                json.dump(logs, f, indent=4)
        
            # log main metric
            accs = [info['r'] for info in infos]
            cnt_avg += sum(accs) / len(accs)
            cnt_any += any(accs)
            print(i, 'sum(accs)', sum(accs), 'cnt_avg', cnt_avg, 'cnt_any', cnt_any, '\n')

    n = args.task_end_index - args.task_start_index
    if args.algorithm == 'whole_tree':
        # store graph to json
        print(graph_list)
        with open(os.path.join(folder_name,'graph.json'), 'w') as file:
            graph_json_str = jsonpickle.encode(graph_list)
            print(graph_json_str)
            file.write(graph_json_str)
            # json.dump(jsonpickle.encode(graph_list, make_refs=False), file, indent=4)

        print(bfs_cnt_avg / n, dfs_cnt_avg / n)
        record.Record_txt(record.acc_file_name, '\nbfs: acc: ' + str(bfs_cnt_avg) + ', acc avg: ' + str(bfs_cnt_avg / n))
        record.Record_txt(record.acc_file_name, '\ndfs+sd: acc: ' + str(dfs_cnt_avg) + ', acc avg: ' + str(dfs_cnt_avg / n))
        record.Record_txt(record.acc_file_name, '\ndfs+ksd: acc: ' + str(ksd_cnt_avg) + ', acc avg: ' + str(ksd_cnt_avg / n))
        record.Record_txt(record.acc_file_name, '\nfsd: acc: ' + str(fsd_cnt_avg) + ', acc avg: ' + str(fsd_cnt_avg / n))
        record.Record_txt(record.acc_file_name, '\navg cost time at each layer: ' + str(nodes_avg_time_per_layer))
        record.Record_txt(record.acc_file_name, '\ntotal cost time: ' + str(total_cost_time) + '\nusage: ' + str(gpt_usage(args.backend)) + '\n')
    else:
        print(cnt_avg / n, cnt_any / n)
        record.Record_txt(record.acc_file_name, '\nacc: ' + str(cnt_avg) + ', acc avg: ' + str(cnt_avg / n) + '\ntotal cost time: ' + str(total_cost_time) + '\nusage: ' + str(gpt_usage(args.backend)) + '\n')
    print('usage_so_far', gpt_usage(args.backend))

def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--backend', type=str, choices=['gpt-4', 'gpt-3.5-turbo'], default='gpt-3.5-turbo')
    args.add_argument('--temperature', type=float, default=0.7)

    args.add_argument('--task', type=str, required=True, choices=['game24', 'text', 'crosswords'])
    args.add_argument('--task_start_index', type=int, default=900)
    args.add_argument('--task_end_index', type=int, default=1000)

    args.add_argument('--naive_run', action='store_true')
    args.add_argument('--prompt_sample', type=str, choices=['standard', 'cot'])  # only used when method_generate = sample, or naive_run

    args.add_argument('--method_generate', type=str, choices=['sample', 'propose'])
    args.add_argument('--method_evaluate', type=str, choices=['value', 'vote'])
    args.add_argument('--method_select', type=str, choices=['sample', 'greedy'], default='greedy')
    args.add_argument('--n_generate_sample', type=int, default=1)  # only thing needed if naive_run
    args.add_argument('--n_evaluate_sample', type=int, default=1)
    args.add_argument('--n_select_sample', type=int, default=1) # b
    args.add_argument('--k', type = int, default = 1) # k
    args.add_argument('--algorithm', type=str, required=True, choices=['bfs', 'dfs+sd', 'dfs+ksd', 'whole_tree', 'fsd_2', 'fsd_graph', 'no_algorithm']) # (bfs, dfs+sd, dfs+ksd, whole_tree, fsd_2)
    args.add_argument('--name_of_task', type=str, default='default')
    args.add_argument('--graph_json', action='store_true')
    
    args = args.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    run(args)