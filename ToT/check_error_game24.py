import json
import pandas as pd
import argparse
import os
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter

from tot.tasks import get_task

excel_file = 'analysis.xlsx'

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

def Init(args):
    path = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}'
    if os.path.exists(os.path.join(path, excel_file)) == False:
        wb = Workbook()
        wb.save(excel_file)
    else:
        wb = load_workbook(excel_file)
    return wb

def error_cot(states, task):
    theoretical = 0
    actual = 0
    correct_list = [0 for _ in range(args.task_end_index - args.task_start_index)]
    for state in states:
        ans = state['ys'][0]
        if 'Answer' not in ans:
            continue
        # if has answer means final number == 24
        theoretical += 1
        correct_list[state['idx'] - 900] = 1
        correct = task.test_output(state['idx'], ans)['r']
        if correct == 1:
            actual += 1
    return theoretical, actual, correct_list

def no_ans_in_base(tree):
    has_ans_list = [0 for _ in range(args.task_end_index - args.task_start_index)]
    for state in tree:
        for step in state['steps']:
            if step['step'] == 2:
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

    no_ans_count = sum(1 for num in has_ans_list if num == 0)
    return has_ans_list, no_ans_count

def wrong_path(has_ans_list, correct_list, impossible):
    wrong_path_count = 0
    for i in range(args.task_end_index - args.task_start_index):
        if has_ans_list[i] == 0 and correct_list[i] == 1:
            impossible += 1
        elif has_ans_list[i] == 1 and correct_list[i] == 0:
            print(i + 900)
            wrong_path_count += 1
    return wrong_path_count, impossible

def append_data(ws, algorithm_name, task_name, theoretical, actual, traversal_nodes, no_ans_in_base, wrong_path, error_cot, task_number):
    # check to append header
    has_header = 0
    blank_count = 0
    pos = 1
    title_pos = 0
    while blank_count == 0 and has_header == 0:
        # print(ws[f'A{pos}'].value)
        if ws[f'A{pos}'].value == algorithm_name:
            has_header = 1
            continue
        if ws[f'A{pos}'].value == None:
            blank_count = 1
            continue
        else:
            blank_count = 0
        pos += 1
    title_pos = pos
    if has_header == 0:
        append_header(ws, algorithm_name, pos)
    pos += 1
    # check to append task row
    has_task = 0
    blank_count = 0
    while has_task == 0 and blank_count == 0:
        if ws[f'A{pos}'].value == task_name:
            has_task = 1
            continue
        if ws[f'A{pos}'].value == None:
            blank_count = 1
            continue
        else:
            blank_count = 0
        pos += 1
    
    if has_task == 0:
        ws[f'A{pos}'].value = task_name
        ws.insert_rows(pos + 1)
    # append theoretical data
    col = find_table_pos(ws, 'theoretical', title_pos)
    col += 1 + task_number
    ws[get_column_letter(col) + str(pos)].value = theoretical
    # append actual data
    col = find_table_pos(ws, 'actual', title_pos)
    col += 1 + task_number
    ws[get_column_letter(col) + str(pos)].value = actual
    # append traversal_nodes data
    col = find_table_pos(ws, 'traversal_nodes', title_pos)
    col += 1 + task_number
    ws[get_column_letter(col) + str(pos)].value = traversal_nodes
    # append no_ans_in_base data
    col = find_table_pos(ws, 'no_ans_in_tree', title_pos)
    col += 1 + task_number
    ws[get_column_letter(col) + str(pos)].value = no_ans_in_base
    # append wrong_path data
    col = find_table_pos(ws, 'wrong_path', title_pos)
    col += 1 + task_number
    ws[get_column_letter(col) + str(pos)].value = wrong_path
    # append error_cot data
    col = find_table_pos(ws, 'error_cot', title_pos)
    col += 1 + task_number
    ws[get_column_letter(col) + str(pos)].value = error_cot

    #count avg
    count_avg(ws, title_pos)

def find_table_pos(ws, title, pos, initial_col = 1):    
    col = initial_col
    blank_count = 0
    while ws[get_column_letter(col) + str(pos)].value != title and blank_count < 2:
        # print(ws[get_column_letter(col) + str(pos)].value)
        col += 1
        if ws[get_column_letter(col) + str(pos)].value == None:
            blank_count += 1
        else:
            blank_count = 0
    
    if blank_count == 2:
        return -1
    return col

def __table__(ws, title, pos, col):
    ws[get_column_letter(col) + str(pos)].value = title
    col += 1
    for i in range(3):
        ws[get_column_letter(col) + str(pos)].value = i
        col += 1
    ws[get_column_letter(col) + str(pos)].value = 'avg'
    col += 1
    # ws[get_column_letter(col) + str(pos)].value = None
    col += 1
    return ws, col

def count_avg(ws, title_pos):
    col = 1
    for i in range(200):
        col = find_table_pos(ws, 'avg', title_pos, col + 1)
        if col == -1:
            break
        ws = __count_avg__(ws, title_pos, col)

def __count_avg__(ws, pos, col):
    pos += 1
    sum = 0
    base = 0
    for i in range(3):
        if ws[get_column_letter(col - i - 1) + str(pos)].value == None:
            continue
        else:
            sum += ws[get_column_letter(col - i - 1) + str(pos)].value
            base += 1
    if base == 0:
        ws[get_column_letter(col) + str(pos)].value = 0
    else:
        ws[get_column_letter(col) + str(pos)].value = sum / base
    return ws

def append_header(ws, task_name, pos):
    # header
    col = 1
    ws[get_column_letter(col) + str(pos)].value = task_name
    col += 1
    # theoretical
    ws, col = __table__(ws, 'theoretical', pos, col)
    # actual
    ws, col = __table__(ws, 'actual', pos, col)
    # traversal nodes
    ws, col = __table__(ws, 'traversal_nodes', pos, col)
    # no ans in tree
    ws, col = __table__(ws, 'no_ans_in_tree', pos, col)
    # error cot
    ws, col = __table__(ws, 'error_cot', pos, col)
    # wrong path
    ws, col = __table__(ws, 'wrong_path', pos, col)

def run(args):
    # load excel file
    wb = Init(args)
    ws = wb.active

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

            bfs_traversal_nodes = sum([state['traversal_nodes'] for state in bfs]) / len(bfs)
            dfs_traversal_nodes = sum([state['traversal_nodes'] for state in dfs]) / len(dfs)

            # error cot
            # bfs
            bfs_theoretical, bfs_actual, bfs_correct_list = error_cot(bfs, task)
            print(f'bfs (theoretical, actual): ({bfs_theoretical, bfs_actual})')
            # dfs
            dfs_theoretical, dfs_actual, dfs_correct_list = error_cot(dfs, task)
            print(f'dfs (theoretical, actual): ({dfs_theoretical, dfs_actual})')

            # no ans in base
            has_ans_list, no_ans_count = no_ans_in_base(base)
            print(has_ans_list)
            print('no ans tree count: ' + str(no_ans_count))

            impossible = 0
            # wrong path bfs
            bfs_wrong_path_count, impossible = wrong_path(has_ans_list, bfs_correct_list, impossible)
            print('bfs wrong path count: ' + str(bfs_wrong_path_count))
            
            # wrong path dfs
            dfs_wrong_path_count, impossible = wrong_path(has_ans_list, dfs_correct_list, impossible)
            print('dfs wrong path count: ' + str(dfs_wrong_path_count))
            print('impossible: ' + str(impossible))

            # output as excel file
            append_data(ws, 'bfs', f'k{args.k}b{args.n_select_sample}', bfs_theoretical, bfs_actual, bfs_traversal_nodes, no_ans_count, bfs_wrong_path_count, bfs_theoretical - bfs_actual, int(name))
            append_data(ws, 'dfs', f'k{args.k}b{args.n_select_sample}', dfs_theoretical, dfs_actual, dfs_traversal_nodes, no_ans_count, dfs_wrong_path_count, dfs_theoretical - dfs_actual, int(name))

    wb.save(os.path.join(path, excel_file))
    print('output as excel file')


if __name__ == '__main__':
    args = parse_args()
    print(args)
    run(args)