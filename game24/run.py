import pandas as pd
import json
import parameters
import llm_function
import game24_draw as draw
from bfs import *
from dfs import *
import record_function as record
import sympy
import re
import time
import model_download
import datetime


def Acc(answer, data, puzzles_id):
    numbers = re.findall(r'\d+', answer)
    problem_numbers = re.findall(r'\d+', data['Puzzles'][puzzles_id])
    if sorted(numbers) != sorted(problem_numbers):
        return False
    return bool(sympy.simplify(answer) == 24)


if __name__ == '__main__':
    # initialize
    data_game24 = pd.read_csv(parameters.data_path_game24)
    locs = list()
    # model_download.Model_download(parameters.repo_id, parameters.model_name, parameters.local_dir)
    llm = llm_function.get_llm()
    acc_count = 0
    total_cost_time = 0
    
    print('llm ok')
    record.Init_record_file(parameters.all_json_file_name, '')
    record.Init_record_file(parameters.acc_file_name, 'model: ' + parameters.huggingface_model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' + str(parameters.evaluator_temperature) + '\ndate: ' + str(datetime.date.today()) + '\nquestions index: ' + str(parameters.initial_idx) + '-' + str(parameters.initial_idx + parameters.question_sets) + '\nmethod: ' + parameters.method + '\n\n')
    parameters.reset_idx()
    for i in range(parameters.initial_idx, parameters.initial_idx + parameters.question_sets):
        #call llm
        start_time = time.time()
        nodes = [{'id': parameters.id, 'answer': data_game24['Puzzles'][i], 'value': None, 'parent_node': None, 'ancestor_value': None}]
        parameters.increase_id()
        if parameters.method == 'bfs':
            record.Init_record_file(parameters.file_name, parameters.huggingface_model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' +  str(parameters.evaluator_temperature) + '\ndate: ' + str(datetime.date.today()) + '\n\n')
            record.Init_record_file(parameters.json_file_name, '')
            loc = bfs(llm, nodes)
        elif parameters.method == 'dfs':
            parameters.reset_t()
            record.Init_record_file(parameters.file_name, parameters.huggingface_model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' +  str(parameters.evaluator_temperature) + '\ndate: ' + str(datetime.date.today()) + '\n\n')
            record.Init_record_file(parameters.json_file_name, '')
            loc = dfs(llm, nodes)
        elif parameters.method == 'dfs+sd':
            parameters.reset_t()
            record.Init_record_file(parameters.file_name, parameters.huggingface_model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' +  str(parameters.evaluator_temperature) + '\ndate: ' + str(datetime.date.today()) + '\n\n')
            record.Init_record_file(parameters.json_file_name, '')
            loc = dfs(llm, nodes, sd = True)
        elif parameters.method == 'dfs+ksd':
            record.Init_record_file(parameters.file_name, parameters.huggingface_model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' +  str(parameters.evaluator_temperature) + '\ndate: ' + str(datetime.date.today()) + '\n\n')
            record.Init_record_file(parameters.json_file_name, '')
            graph = tree_graph.graph()
            level_nodes = [[]] * (parameters.T + 1)
            # Greedy to define d_thres
            print(level_nodes)
            best_node, max_value = Greedy(llm, nodes, graph, level_nodes=level_nodes)
            print(level_nodes)
            loc = ksd(llm, nodes, max_value, best_node, d_thres, level_nodes, graph)
        end_time = time.time()
        # record
        loc['id'] = i
        loc['correct'] = Acc(loc['answer'], data_game24, i)
        loc['cost time'] = end_time - start_time
        if parameters.model_import_method == 'openai':
            loc['cost'] = llm_function.openai_usage()
        locs.append(loc)
        record.Record_json(parameters.json_file_name, loc)
        # print(loc)
        record.Record_txt(parameters.acc_file_name, 'id ' + str(i) + ': ' + data_game24['Puzzles'][i] + ', ' + loc['answer'] + '\n')
        if loc['correct'] == True:
            acc_count += 1
        total_cost_time += loc['cost time']
        parameters.increase_idx()
        parameters.reset_id()
    record.Record_json(parameters.all_json_file_name, locs)
    record.Record_txt(parameters.acc_file_name, '\nacc: ' + str(acc_count) + '\ntotal cost time: ' + str(total_cost_time))
    # draw
    if parameters.method == 'bfs' or parameters.method == 'dfs+ksd':
        draw.bfs_Draw(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))
    if parameters.method == 'dfs' or parameters.method == 'dfs+sd':
        draw.dfs_Draw(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))
