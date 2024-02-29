import pandas as pd
import json
import parameters
import llm_function
import crosswords_draw as draw
from dfs import *
import record_function as record
import re
import time
import model_download
import datetime
import crosswords_function as crosswords
import acc
import dfs_sd as sd
import dfs_ksd as ksd

if __name__ == '__main__':
    llm = llm_function.get_llm()
    locs = list()
    acc_letter_count = 0
    acc_word_count = 0
    acc_game_count = 0
    total_cost_time = 0

    print('llm ok')
    record.Init_record_file(parameters.all_json_file_name, '')
    record.Init_record_file(parameters.acc_file_name, 'model: ' + parameters.huggingface_model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' + str(parameters.evaluator_temperature) + '\ndate: ' + str(datetime.date.today()) + '\nquestions index: ' + str(parameters.initial_idx) + '-' + str(parameters.initial_idx + parameters.question_sets - 1) + '\nmethod: ' + parameters.method + '\n\n')
    parameters.reset_idx()

    for i in range(parameters.initial_idx, parameters.initial_idx + parameters.question_sets):
        # initialize
        record.Init_record_file(parameters.file_name, parameters.model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' + str(parameters.evaluator_temperature) + '\ndata: ' + str(datetime.date.today()) + '\nquestions index: ' + str(parameters.initial_idx) + '-' + str(parameters.initial_idx + parameters.question_sets - 1) + '\nmethod: ' + parameters.method + '\n\n')
        record.Init_record_file(parameters.json_file_name, '')
        crosswords.env.reset()
        nodes = [{'id': crosswords.env.get_id(), 'answer': None, 'value': None, 'parent_node': None, 'ancestor_value': None, 'ancestor_distance': None}]
        #call dfs
        start_time = time.time()
        if parameters.method == 'tot-dfs':
            loc = dfs(llm, nodes)
        elif parameters.method == 'dfs+sd':
            loc = sd.dfs(llm, nodes, sd = True)
        elif parameters.method == 'dfs+ksd':
            loc = ksd.ksd(llm, nodes)
        end_time = time.time()
        # record
        loc['id'] = parameters.idx
        loc['cost time'] = end_time - start_time
        loc['correct'] = acc.acc(loc['answer'], parameters.idx)
        if parameters.model_import_method == 'openai':
            loc['cost'] = llm_function.openai_usage()
        locs.append(loc)
        record.Record_json(parameters.json_file_name, loc)
        acc_letter_count += loc['correct']['letter'] 
        acc_word_count += loc['correct']['word']
        acc_game_count += loc['correct']['game']
        total_cost_time += loc['cost time']
        print(loc)
        crosswords.env.reset()
        parameters.increase_idx()
    record.Record_txt(parameters.acc_file_name, '\nacc: ' + str(acc_letter_count / (parameters.question_sets * 25)) + ', ' + str(acc_word_count / parameters.question_sets) + ', ' + str(acc_game_count) + '\ntotal cost time: ' + str(total_cost_time))
    record.Record_json(parameters.all_json_file_name, locs)
    draw.Draw(parameters.all_json_file_name.format(file_path = parameters.record_files_folder))
