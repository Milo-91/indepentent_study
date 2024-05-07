import os
import json
import argparse
import tot.record_functions as record
import datetime
import time

from tot.tasks import get_task
from tot.tasks import draw
import tot.tasks.tree_graph as tree_graph
from tot.methods.bfs import solve, naive_solve
from tot.methods.bfs_2 import bfs
from tot.methods.dfs_sd import dfs
from tot.methods.dfs_ksd import ksd
from tot.methods.whole_tree import build
from tot.models import gpt_usage

def run(args):
    task = get_task(args.task)
    logs, cnt_avg, cnt_any = [], 0, 0
    bfs_cnt_avg = 0
    dfs_cnt_avg = 0
    total_cost_time = 0
    folder_index = 0
    folder_name = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}/{folder_index}'
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
                ys, info = bfs(args, task, i)
        elif args.algorithm == 'dfs+sd':
            ys, info, traversal_nodes = dfs(args, task, i, sd = True, sorting = True, high_acc_mode = False)
        elif args.algorithm == 'dfs+ksd':
            ys, info, traversal_nodes = ksd(args, task, i)
        elif args.algorithm == 'whole_tree':
            graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = i)
            ys, info, traversal_nodes = build(args, task, i, graph = graph)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            bfs_ys, bfs_info, bfs_traversal_nodes = bfs(args, task, i, graph = graph)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            dfs_ys, dfs_info, dfs_traversal_nodes = dfs(args, task, i, sd = True, sorting = True, high_acc_mode = False, graph = graph)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
        end_time = time.time()
        print(end_time - start_time)
        total_cost_time += end_time - start_time
        if args.algorithm == 'whole_tree':
            record.Record_txt(record.record_file_name, '\nbfs_ys = ' + str(bfs_ys) + '\ndfs_ys = ' + str(dfs_ys) + '\n\n', idx = i)
        else:
            record.Record_txt(record.record_file_name, '\nys = ' + str(ys) + '\n\n', idx = i)
        record.Record_txt(record.record_file_name, '\n-----task complete-----\n', idx = i)
        # log
        if args.algorithm == 'whole_tree':
            bfs_infos = [task.test_output(i, y) for y in bfs_ys]
            dfs_infos = [task.test_output(i, y) for y in dfs_ys]
            info.update({'idx': i, 'traversal_nodes': traversal_nodes})
            bfs_info.update({'idx': i, 'ys': bfs_ys, 'infos': bfs_infos, 'traversal_nodes': bfs_traversal_nodes, 'usage_so_far': gpt_usage(args.backend)}) # even
            dfs_info.update({'idx': i, 'ys': dfs_ys, 'infos': dfs_infos, 'traversal_nodes': dfs_traversal_nodes, 'usage_so_far': gpt_usage(args.backend)}) # odd
            record.Record_txt(record.record_file_name, '\nbfs_ys: ' + str(bfs_ys)  + ', infos: ' + str(bfs_infos) + '\ndfs_ys: ' + str(dfs_ys) + ', infos: ' + str(dfs_infos) + '\n\n', idx = i) 
            record.Record_txt(record.record_file_name, '\ncost time: ' + str(end_time - start_time) + '\n\n', idx = i)
            record.Record_txt(record.acc_file_name, str(i) + '\n\b bfs_ys: ' + str(bfs_ys[0])  + ', acc: ' + str(bfs_infos[0]) + ', traversal nodes: ' + str(bfs_traversal_nodes) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs_ys: ' + str(dfs_ys[0])  + ', acc: ' + str(dfs_infos[0]) + ', traversal nodes: ' + str(dfs_traversal_nodes) + '\n\n')
            logs.append(info)
            logs.append(bfs_info)
            logs.append(dfs_info)
            with open(file, 'w') as f:
                json.dump(logs, f, indent=4)

            # log main metric
            bfs_accs = [info['r'] for info in bfs_infos]
            dfs_accs = [info['r'] for info in dfs_infos]
            bfs_cnt_avg += sum(bfs_accs) / len(bfs_accs)
            print(i, 'bfs: sum(accs)', sum(bfs_accs), 'cnt_avg', bfs_cnt_avg, '\n')
            dfs_cnt_avg += sum(dfs_accs) / len(dfs_accs)
            print(i, 'dfs: sum(accs)', sum(dfs_accs), 'cnt_avg', dfs_cnt_avg, '\n')
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
        print(bfs_cnt_avg / n, dfs_cnt_avg / n)
        record.Record_txt(record.acc_file_name, '\nbfs: acc: ' + str(bfs_cnt_avg) + ', acc avg: ' + str(bfs_cnt_avg / n))
        record.Record_txt(record.acc_file_name, '\ndfs: acc: ' + str(bfs_cnt_avg) + ', acc avg: ' + str(dfs_cnt_avg / n) + '\ntotal cost time: ' + str(total_cost_time) + '\nusage: ' + str(gpt_usage(args.backend)) + '\n')
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
    args.add_argument('--algorithm', type=str, required=True, choices=['bfs', 'dfs+sd', 'dfs+ksd', 'whole_tree']) # (bfs, dfs+sd, dfs+ksd, whole_tree)
    args.add_argument('--name_of_task', type=str, default='default')

    args = args.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    run(args)