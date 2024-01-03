import pandas as pd
import json
import parameters
import llm_function
from dfs import *
import record_function as record
import re
import time
import crosswords_function as crosswords


if __name__ == '__main__':
    llm = llm_function.get_llm()
    locs = list()
    print('llm ok')
    record.Init_record_file(parameters.all_json_file_name, '')
    for i in range(1):
        # initialize
        record.Init_record_file(parameters.file_name, parameters.model_path + '\ntemperature: ' + str(parameters.temperature) + '\n')
        record.Init_record_file(parameters.json_file_name, '')
        crosswords.env.reset()
        nodes = [{'id': crosswords.env.get_id(), 'answer': None, 'value': None, 'parent_node': None, 'ancestor_value': None}]
        #call dfs
        start_time = time.time()
        loc = dfs(llm, nodes)
        end_time = time.time()
        # record
        loc['id'] = parameters.idx
        loc['cost time'] = end_time - start_time
        locs.append(loc)
        record.Record_json(parameters.json_file_name, loc)
        print(loc)
        crosswords.env.reset()
        parameters.increase_idx()
    record.Record_json(parameters.all_json_file_name, locs)