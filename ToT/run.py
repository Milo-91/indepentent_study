import os
import json
import argparse
import tot.record_functions as record
import datetime
import time

from tot.tasks import get_task
from tot.methods.bfs import solve, naive_solve
from tot.methods.dfs_sd import dfs
from tot.models import gpt_usage

def run(args):
    task = get_task(args.task)
    logs, cnt_avg, cnt_any = [], 0, 0
    total_cost_time = 0
    if args.naive_run:
        file = f'./logs/{args.task}/{args.backend}_{args.temperature}_naive_{args.prompt_sample}_sample_{args.n_generate_sample}_start{args.task_start_index}_end{args.task_end_index}.json'
    else:
        file = f'./logs/{args.task}/{args.backend}_{args.temperature}_{args.method_generate}{args.n_generate_sample}_{args.method_evaluate}{args.n_evaluate_sample}_{args.method_select}{args.n_select_sample}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}.json'
    os.makedirs(os.path.dirname(file), exist_ok=True)
    record.Init_record_file(record.acc_file_name, f'model: {args.backend}\ntemperature: {args.temperature}\nalgorithm: {args.algorithm}\nk: {args.k}\nb: {args.n_select_sample}\nstart_index: {args.task_start_index}\nend_index: {args.task_end_index}\ndate: {datetime.date.today()}\n\n')
    print('start task')
    for i in range(args.task_start_index, args.task_end_index):
        traversal_nodes = 0
        record.Init_record_file(record.record_file_name, f'model: {args.backend}\ntemperature: {args.temperature}\nalgorithm: {args.algorithm}\nk: {args.k}\nb: {args.n_select_sample}\nidx: {i}\ndate: {datetime.date.today()}\n\n', idx = i)
        # reset id
        task.reset_id()
        # solve
        start_time = time.time()
        if args.algorithm == 'bfs':
            if args.naive_run:
                ys, info = naive_solve(args, task, i) 
            else:
                ys, info = solve(args, task, i)
        elif args.algorithm == 'dfs+sd':
            ys, info, traversal_nodes = dfs(args, task, i, sd = True, sorting = True, high_acc_mode = False)
        end_time = time.time()
        print(end_time - start_time)
        total_cost_time += end_time - start_time
        record.Record_txt(record.record_file_name, '\nys = ' + str(ys) + '\n\n', idx = i)
        record.Record_txt(record.record_file_name, '\n-----task complete-----\n', idx = i)
        # log
        infos = [task.test_output(i, y) for y in ys]
        info.update({'idx': i, 'ys': ys, 'infos': infos, 'traversal_nodes': traversal_nodes, 'usage_so_far': gpt_usage(args.backend)}) # bfs no traversal nodes
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
    args.add_argument('--algorithm', type=str, default='bfs') # (bfs, dfs+sd)

    args = args.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    run(args)