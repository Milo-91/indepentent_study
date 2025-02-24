import os
import json
import argparse
import datetime
import time
import copy
import sys
import jsonpickle

from tot.tasks import get_task
from tot.models import gpt_usage
from tot.tasks import draw
import tot.tasks.tree_graph as tree_graph
import tot.record_functions as record
from tot.methods.whole_tree import build
from tot.methods.evaluator import evaluation
from tot.methods.bfs_2 import bfs
from tot.methods.dfs_sd import dfs
from tot.methods.dfs_ksd import ksd

def error_log(type, value, traceback):
    print(f'type: {type}, value: {value}, traceback: {traceback}')
    with open('error.log', 'a') as file:
        file.write(f'type: {type}  value: {value}  traceback: {traceback}\n')

def run(args):
    # error log
    sys.excepthook = error_log
    # initialize
    task = get_task(args.task)
    logs, cnt_avg, cnt_any = [], 0, 0
    bfs_cnt_avg = 0
    dfs_cnt_avg = 0
    ksd_cnt_avg = 0
    graph_list = []
    nodes_avg_time_per_layer = [0, 0, 0]
    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', indent=4)
    # folder_index for avoid collision
    folder_index = 0
    folder_name = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}/{folder_index}'
    json_file_name = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_{args.evaluator_method}.json')
    json_file_name_origin = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_origin.json')
    json_file_name_logprob = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_logprob.json')
    while os.path.exists(folder_name)and any(file.endswith('.json') for file in os.listdir(folder_name)):
        folder_index += 1
        folder_name = f'./logs/{args.task}/{args.name_of_task}/k{args.k}b{args.n_select_sample}/{folder_index}'
        if args.evaluator_method == 'compare':
            json_file_name_origin = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_origin.json')
            json_file_name_logprob = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_logprob.json')                        
        else:
            json_file_name = os.path.join(folder_name, f'{args.name_of_task}_start{args.task_start_index}_end{args.task_end_index}_{args.algorithm}_{args.evaluator_method}.json')
    os.makedirs(os.path.dirname(folder_name), exist_ok=True)
    record.Init_folder_path(folder_name)
    draw.Init_image_folder_path(folder_name)
    print('start task')
    
    # task
    for i in range(args.task_start_index, args.task_end_index):
        traversal_nodes = 0
        record.Init_record_file(record.record_file_name, f'model: {args.backend}\ntemperature: {args.temperature}\nalgorithm: {args.algorithm}\nk: {args.k}\nb: {args.n_select_sample}\nidx: {i}\ndate: {datetime.date.today()}\n\n', idx = i)
        # for each task which needs to reset initialize id
        task.reset_id()

        # solve
        graph = tree_graph.graph(k = args.k, b = args.n_select_sample, idx = i)
        # for reuse graph by json file
        # if args.graph_json == True:
        #     record.Record_txt(record.record_file_name, '\nuse json to load graph\n', idx = i)
        #     graph.__load_from_json__('graph.json', i - 900)
        #     print('id: ' + str(len(graph.nodes)))
        #     task.reset_id(id = len(graph.nodes))
        if args.evaluator_method == 'compare':
            # for list [0: bfs, 1: dfs+sd, 2: ksd][0: origin, 1: logprob]
            ys_list = [[{} for _ in range(2)] for _ in range(3)]
            info_list = [[{} for _ in range(2)] for _ in range(3)]
            traversal_nodes_list = [[{} for _ in range(2)] for _ in range(3)]
            cost_time_list = [[{} for _ in range(2)] for _ in range(3)]
            # building complete tree
            print('-----building tree start-----')
            info, traversal_nodes = build(args, task, i, graph = graph)
            print('-----building tree end-----')
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)

            # ---------- origin ----------

            # evaluation
            print('-----evaluation start-----')
            graph_origin = copy.copy(graph)
            graph_origin.show_in_nodes()
            args.evaluator_method = 'origin'
            evaluation(args, task, i, graph_origin)
            print('-----evaluation end-----')
            # algorithm
            graph_origin_copy = copy.copy(graph_origin)
            graph_origin.show_in_nodes()
            ys_list[0][0], info_list[0][0], traversal_nodes_list[0][0], cost_time_list[0][0] = bfs(args, task, i, graph = graph_origin_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_origin_copy = copy.copy(graph_origin)
            graph_origin.show_in_nodes()
            task.reset_id(id = traversal_nodes)
            ys_list[1][0], info_list[1][0], traversal_nodes_list[1][0], cost_time_list[1][0] = dfs(args, task, i, graph = graph_origin_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_origin_copy = copy.copy(graph_origin)
            graph_origin.show_in_nodes()
            task.reset_id(id = traversal_nodes)
            ys_list[2][0], info_list[2][0], traversal_nodes_list[2][0], cost_time_list[2][0] = ksd(args, task, i, graph = graph_origin_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_origin.show_in_nodes()
            record.Record_txt(record.record_file_name, '\norigin\nbfs_ys = ' + str(ys_list[0][0]) + '\ndfs+sd_ys = ' + str(ys_list[1][0]) + '\ndfs+ksd_ys = ' + str(ys_list[2][0]) + '\n\n', idx = i)
            
            # log
            infos = [[None for _ in range(2)] for _ in range(3)]
            infos[0][0] = [task.test_output(i, y) for y in ys_list[0][0]]
            infos[1][0] = [task.test_output(i, y) for y in ys_list[1][0]]
            infos[2][0] = [task.test_output(i, y) for y in ys_list[2][0]]
            info.update({'idx': i, 'traversal_nodes': traversal_nodes})                                                                                                                                              # %4 0
            info_list[0][0].update({'idx': i, 'ys': ys_list[0][0], 'infos': infos[0][0], 'traversal_nodes': traversal_nodes_list[0][0], 'cost time': cost_time_list[0][0], 'usage_so_far': gpt_usage(args.backend)}) # %4 1
            info_list[1][0].update({'idx': i, 'ys': ys_list[1][0], 'infos': infos[1][0], 'traversal_nodes': traversal_nodes_list[1][0], 'cost time': cost_time_list[1][0], 'usage_so_far': gpt_usage(args.backend)}) # %4 2
            info_list[2][0].update({'idx': i, 'ys': ys_list[2][0], 'infos': infos[2][0], 'traversal_nodes': traversal_nodes_list[2][0], 'cost time': cost_time_list[2][0], 'usage_so_far': gpt_usage(args.backend)}) # %4 3
            record.Record_txt(record.record_file_name, '\nbfs_ys: ' + str(ys_list[0][0])  + ', infos: ' + str(infos[0][0]) + '\ndfs+sd_ys: ' + str(ys_list[1][0]) + ', infos: ' + str(infos[1][0]) + '\ndfs+ksd_ys: ' + str(ys_list[2][0]) + ', infos: ' + str(infos[2][0]) + '\n\n', idx = i) 
            record.Record_txt(record.acc_file_name, str(i) + '\n\b bfs_ys: ' + str(ys_list[0][0][0])  + ', acc: ' + str(infos[0][0][0]) + ', traversal nodes: ' + str(traversal_nodes_list[0][0]) + ', cost time: ' + str(cost_time_list[0][0]) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+sd_ys: ' + str(ys_list[1][0][0])  + ', acc: ' + str(infos[1][0][0]) + ', traversal nodes: ' + str(traversal_nodes_list[0][0]) + ', cost time: ' + str(cost_time_list[1][0]) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+ksd_ys: ' + str(ys_list[2][0][0])  + ', acc: ' + str(infos[2][0][0]) + ', traversal nodes: ' + str(traversal_nodes_list[2][0]) + ', cost time: ' + str(cost_time_list[2][0]) + '\n\n')
            logs.append(info)
            logs.append(info_list[0][0])
            logs.append(info_list[1][0])
            logs.append(info_list[2][0])
            with open(json_file_name_origin, 'w') as f:
                json.dump(logs, f, indent=4)
            
            # ---------- logprob ----------

            # evaluation
            print('-----evaluation start-----')
            graph_logprob = copy.copy(graph)
            graph_logprob.show_in_nodes()
            args.evaluator_method = 'logprob'
            evaluation(args, task, i, graph_logprob)
            print('-----evaluation end-----')
            graph_logprob_copy = copy.copy(graph_logprob)
            graph_logprob.show_in_nodes()
            task.reset_id(id = traversal_nodes)
            ys_list[0][1], info_list[0][1], traversal_nodes_list[0][1], cost_time_list[0][1] = bfs(args, task, i, graph = graph_logprob_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_logprob_copy = copy.copy(graph_logprob)
            graph_logprob.show_in_nodes()
            task.reset_id(id = traversal_nodes)
            ys_list[1][1], info_list[1][1], traversal_nodes_list[1][1], cost_time_list[1][1] = dfs(args, task, i, graph = graph_logprob_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_logprob_copy = copy.copy(graph_logprob)
            graph_logprob.show_in_nodes()
            task.reset_id(id = traversal_nodes)
            ys_list[2][1], info_list[2][1], traversal_nodes_list[2][1], cost_time_list[2][1] = ksd(args, task, i, graph = graph_logprob_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            record.Record_txt(record.record_file_name, '\nlogprob\nbfs_ys = ' + str(ys_list[0][1]) + '\ndfs+sd_ys = ' + str(ys_list[1][1]) + '\ndfs+ksd_ys = ' + str(ys_list[2][1]) + '\n\n', idx = i)

            # log 
            infos[0][1] = [task.test_output(i, y) for y in ys_list[0][1]]
            infos[1][1] = [task.test_output(i, y) for y in ys_list[1][1]]
            infos[2][1] = [task.test_output(i, y) for y in ys_list[2][1]]
            print('-------要不要讓我交報告了-------')
            info_list[0][1].update({'idx': i, 'ys': ys_list[0][1], 'infos': infos[0][1], 'traversal_nodes': traversal_nodes_list[0][1], 'cost time': cost_time_list[0][1], 'usage_so_far': gpt_usage(args.backend)}) # %4 1
            info_list[1][1].update({'idx': i, 'ys': ys_list[1][1], 'infos': infos[1][1], 'traversal_nodes': traversal_nodes_list[1][1], 'cost time': cost_time_list[1][1], 'usage_so_far': gpt_usage(args.backend)}) # %4 2
            info_list[2][1].update({'idx': i, 'ys': ys_list[2][1], 'infos': infos[2][1], 'traversal_nodes': traversal_nodes_list[2][1], 'cost time': cost_time_list[2][1], 'usage_so_far': gpt_usage(args.backend)}) # %4 3
            record.Record_txt(record.record_file_name, '\nbfs_ys: ' + str(ys_list[0][1])  + ', infos: ' + str(infos[0][1]) + '\ndfs+sd_ys: ' + str(ys_list[1][1]) + ', infos: ' + str(infos[1][1]) + '\ndfs+ksd_ys: ' + str(ys_list[2][1]) + ', infos: ' + str(infos[2][1]) + '\n\n', idx = i) 
            record.Record_txt(record.acc_file_name, str(i) + '\n\b bfs_ys: ' + str(ys_list[0][1][0])  + ', acc: ' + str(infos[0][1][0]) + ', traversal nodes: ' + str(traversal_nodes_list[0][1]) + ', cost time: ' + str(cost_time_list[0][1]) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+sd_ys: ' + str(ys_list[1][1][0])  + ', acc: ' + str(infos[1][1][0]) + ', traversal nodes: ' + str(traversal_nodes_list[0][1]) + ', cost time: ' + str(cost_time_list[1][1]) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+ksd_ys: ' + str(ys_list[2][1][0])  + ', acc: ' + str(infos[2][1][0]) + ', traversal nodes: ' + str(traversal_nodes_list[2][1]) + ', cost time: ' + str(cost_time_list[2][1]) + '\n\n')
            print('---------------------0-------------------------')
            logs = []
            print('---------------------1-------------------------')
            logs.append(info)
            print('---------------------2-------------------------')
            logs.append(info_list[0][1])
            print('---------------------3-------------------------')
            logs.append(info_list[1][1])
            print('---------------------4-------------------------')
            logs.append(info_list[2][1])
            print('---------------------5-------------------------')
            with open(json_file_name_logprob, 'w') as f:
                json.dump(logs, f, indent=4)
        else:
            # building complete tree
            print('-----building tree start-----')
            info, traversal_nodes = build(args, task, i, graph = graph)
            print('-----building tree end-----')
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            print('-----evaluation start-----')
            evaluation(args, task, i, graph)
            print('-----evaluation end-----')
            graph_copy = copy.copy(graph)
            graph.show_in_nodes()
            bfs_ys, bfs_info, bfs_traversal_nodes, bfs_cost_time = bfs(args, task, i, graph = graph_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            graph.show_in_nodes()
            dfs_ys, dfs_info, dfs_traversal_nodes, dfs_cost_time = dfs(args, task, i, graph = graph_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            graph.show_in_nodes()
            ksd_ys, ksd_info, ksd_traversal_nodes, ksd_cost_time = ksd(args, task, i, graph = graph_copy)
            record.Record_txt(record.record_file_name, '\nusage so far: ' + str(gpt_usage(args.backend)) + '\n\n', idx = i)
            graph_copy = copy.copy(graph)
            graph_list.append({'total_element': graph.total_element, 'tree_head': graph.tree_head.copy(), 'nodes': graph.nodes.copy(), 'visited': graph.visited.copy(), 'idx': graph.idx})
            record.Record_txt(record.record_file_name, '\nbfs_ys = ' + str(bfs_ys) + '\ndfs+sd_ys = ' + str(dfs_ys) + '\ndfs+ksd_ys = ' + str(ksd_ys) + '\n\n', idx = i)
        
            # log
            bfs_infos = [task.test_output(i, y) for y in bfs_ys]
            dfs_infos = [task.test_output(i, y) for y in dfs_ys]
            ksd_infos = [task.test_output(i, y) for y in ksd_ys]
            
            info.update({'idx': i, 'traversal_nodes': traversal_nodes})                                                                                                                # %4 0
            bfs_info.update({'idx': i, 'ys': bfs_ys, 'infos': bfs_infos, 'traversal_nodes': bfs_traversal_nodes, 'cost time': bfs_cost_time, 'usage_so_far': gpt_usage(args.backend)}) # %4 1
            dfs_info.update({'idx': i, 'ys': dfs_ys, 'infos': dfs_infos, 'traversal_nodes': dfs_traversal_nodes, 'cost time': dfs_cost_time, 'usage_so_far': gpt_usage(args.backend)}) # %4 2
            ksd_info.update({'idx': i, 'ys': ksd_ys, 'infos': ksd_infos, 'traversal_nodes': ksd_traversal_nodes, 'cost time': ksd_cost_time, 'usage_so_far': gpt_usage(args.backend)}) # %4 3
            record.Record_txt(record.record_file_name, '\nbfs_ys: ' + str(bfs_ys)  + ', infos: ' + str(bfs_infos) + '\ndfs+sd_ys: ' + str(dfs_ys) + ', infos: ' + str(dfs_infos) + '\ndfs+ksd_ys: ' + str(ksd_ys) + ', infos: ' + str(ksd_infos) + '\n\n', idx = i) 
            record.Record_txt(record.acc_file_name, str(i) + '\n\b bfs_ys: ' + str(bfs_ys[0])  + ', acc: ' + str(bfs_infos[0]) + ', traversal nodes: ' + str(bfs_traversal_nodes) + ', cost time: ' + str(bfs_cost_time) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+sd_ys: ' + str(dfs_ys[0])  + ', acc: ' + str(dfs_infos[0]) + ', traversal nodes: ' + str(dfs_traversal_nodes) + ', cost time: ' + str(dfs_cost_time) + '\n\n')
            record.Record_txt(record.acc_file_name, '\b dfs+ksd_ys: ' + str(ksd_ys[0])  + ', acc: ' + str(ksd_infos[0]) + ', traversal nodes: ' + str(ksd_traversal_nodes) + ', cost time: ' + str(ksd_cost_time) + '\n\n')
            logs.append(info)
            logs.append(bfs_info)
            logs.append(dfs_info)
            logs.append(ksd_info)
            with open(json_file_name, 'w') as f:
                json.dump(logs, f, indent=4)
            
            # log main metric
            bfs_accs = [info['r'] for info in bfs_infos]
            dfs_accs = [info['r'] for info in dfs_infos]
            ksd_accs = [info['r'] for info in ksd_infos]
            bfs_cnt_avg += sum(bfs_accs) / len(bfs_accs)
            print(i, 'bfs: sum(accs)', sum(bfs_accs), 'cnt_avg', bfs_cnt_avg, '\n')
            dfs_cnt_avg += sum(dfs_accs) / len(dfs_accs)
            print(i, 'dfs: sum(accs)', sum(dfs_accs), 'cnt_avg', dfs_cnt_avg, '\n')
            ksd_cnt_avg += sum(ksd_accs) / len(ksd_accs)
            print(i, 'ksd: sum(accs)', sum(ksd_accs), 'cnt_avg', ksd_cnt_avg, '\n')
        
    n = args.task_end_index - args.task_start_index
    # store graph to json
    print(graph_list)
    with open(os.path.join(folder_name,'graph.json'), 'w') as file:
        graph_json_str = jsonpickle.encode(graph_list)
        print(graph_json_str)
        file.write(graph_json_str)
        # json.dump(jsonpickle.encode(graph_list, make_refs=False), file, indent=4)
    
    record.Record_txt(record.acc_file_name, '\nbfs: acc: ' + str(bfs_cnt_avg) + ', acc avg: ' + str(bfs_cnt_avg / n))
    record.Record_txt(record.acc_file_name, '\ndfs+sd: acc: ' + str(dfs_cnt_avg) + ', acc avg: ' + str(dfs_cnt_avg / n))
    record.Record_txt(record.acc_file_name, '\ndfs+ksd: acc: ' + str(ksd_cnt_avg) + ', acc avg: ' + str(ksd_cnt_avg / n))
    record.Record_txt(record.acc_file_name, '\navg cost time at each layer: ' + str(nodes_avg_time_per_layer))
    record.Record_txt(record.acc_file_name, '\nusage: ' + str(gpt_usage(args.backend)) + '\n')


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
    args.add_argument('--evaluator_method', type=str, choices=['origin', 'logprob', 'compare'], default='origin')
    
    args = args.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    run(args)