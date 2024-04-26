import json
import pandas as pd
import argparse
import os
import re
import sympy

from tot.tasks import get_task


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--task', type=str, required=True, choices=['game24', 'text', 'crosswords'])
    args.add_argument('--task_start_index', type=int, default=900)
    args.add_argument('--task_end_index', type=int, default=1000)
    args.add_argument('--algorithm', type=str, required=True, choices=['bfs', 'dfs+sd', 'dfs+ksd', 'whole_tree']) # (bfs, dfs+sd, dfs+ksd, whole_tree)
    args.add_argument('--n_select_sample', type=int, default=1) # b
    args.add_argument('--k', type = int, default = 1) # k
    args.add_argument('--name_of_task', type=str, default='default')
    args = args.parse_args()
    return args

def run(args):
    task = get_task(args.task)
    path = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}'
    dir_list = os.listdir(path)
    dir_list = [item for item in dir_list if os.path.isdir(os.path.join(path, item))]
    for name in dir_list:
        folder_name = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}/{name}'
        print(folder_name)
        file_name = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_0.json')
        print(file_name)
        with open(file_name, 'r') as file:
             data = json.load(file)

        if args.algorithm == 'whole_tree':
                base = [data[i] for i in range(len(data)) if i % 3 == 0]
                print('\n'.join(map(str, base)))

                bfs = [data[i] for i in range(len(data)) if i % 3 == 1]
                print('\n'.join(map(str, bfs)))

                dfs = [data[i] for i in range(len(data)) if i % 3 == 2]
                print('\n'.join(map(str, dfs)))
                usage_so_far = data['usage_so_far']

                # error cot
                # bfs
                bfs_theoretical = 0
                bfs_actual = 0
                bfs_correct_list = [0 for _ in range(args.task_end_index - args.task_start_index)]
                for state in bfs:
                    ans = state['ys'][0]
                    if 'Answer' not in ans:
                        continue
                    # if has answer means final number == 24
                    bfs_theoretical += 1
                    bfs_correct_list[state['idx'] - 900] = 1
                    correct = task.test_output(state['idx'], ans)['r']
                    if correct == 1:
                        bfs_actual += 1
                print(f'bfs (theoretical, actual): ({bfs_theoretical, bfs_actual})')
                # dfs
                dfs_theoretical = 0
                dfs_actual = 0
                dfs_correct_list = [0 for _ in range(args.task_end_index - args.task_start_index)]
                for state in dfs:
                    ans = state['ys'][0]
                    if 'Answer' not in ans:
                        continue
                    # if has answer means final number == 24
                    dfs_theoretical += 1
                    dfs_correct_list[state['idx'] - 900] = 1
                    correct = task.test_output(state['idx'], ans)['r']
                    if correct == 1:
                        dfs_actual += 1
                print(f'dfs (theoretical, actual): ({dfs_theoretical, dfs_actual})')

                # no ans in base
                has_ans_list = [0 for _ in range(args.task_end_index - args.task_start_index)]
                for state in base:
                    for step in state['steps']:
                        if step['step'] == 3:       
                            leaf_nodes = step['ys']
                    # print(leaf_nodes)
                    for node in leaf_nodes:
                        ans = node[1].split('\n')[-2]
                        # print(ans)
                        if 'left: ' not in ans:
                             continue
                        ans = ans.split('left: ')[-1].replace(')', '').strip()
                        # print(ans)
                        if ans == '24':
                            has_ans_list[state['idx'] - 900] = 1
                print(has_ans_list)
                no_ans_count = sum(1 for num in has_ans_list if num == 0)
                print('no ans tree count: ' + str(no_ans_count))

                impossible = 0
                # wrong path bfs
                bfs_wrong_path_count = 0
                for i in range(args.task_end_index - args.task_start_index):
                    if has_ans_list[i] == 0 and bfs_correct_list[i] == 1:
                        impossible += 1
                    elif has_ans_list[i] == 1 and bfs_correct_list[i] == 0:
                        print(i + 900)
                        bfs_wrong_path_count += 1
                print('bfs wrong path count: ' + str(bfs_wrong_path_count))
                
                # wrong path dfs
                dfs_wrong_path_count = 0
                for i in range(args.task_end_index - args.task_start_index):
                    if has_ans_list[i] == 0 and dfs_correct_list[i] == 1:
                        impossible += 1
                    elif has_ans_list[i] == 1 and dfs_correct_list[i] == 0:
                        print(i + 900)
                        dfs_wrong_path_count += 1
                print('dfs wrong path count: ' + str(dfs_wrong_path_count))
                print('impossible: ' + str(impossible))

                # output as excel file
                output_1 = {
                    'algorithm': ['bfs', 'dfs'],
                    'theoretical': [bfs_theoretical, dfs_theoretical],
                    'actual': [bfs_actual, dfs_actual],
                    'wrong path': [bfs_wrong_path_count, dfs_wrong_path_count]
                }
                output_2 = {
                    'case': ['impossible', 'no ans tree', 'cost'],
                    'value': [impossible, no_ans_count, ]
                }
                df1 = pd.DataFrame(output_1)
                df2 = pd.DataFrame(output_2)

                excel_file = os.path.join(path, 'analysis.xlsx')
                with pd.ExcelWriter(excel_file, engine=None) as writer:
                    df1.to_excel(writer, sheet_name='Sheet1', startrow=0, index=False)
                    df2.to_excel(writer, sheet_name='Sheet1', startrow=df1.shape[0] + 2, index=False)

                print('output as excel file')


if __name__ == '__main__':
    args = parse_args()
    print(args)
    run(args)