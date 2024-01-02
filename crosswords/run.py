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
    for i in range(1):
        start_time = time.time()
        nodes = [{'id': crosswords.env.get_id(), 'answer': None, 'value': None, 'parent_node': None, 'ancestor_value': None}]
        record.Init_record_file(parameters.file_name, parameters.model_path + '\ntemperature: ' + str(parameters.temperature) )
        record.Init_record_file(parameters.json_file_name, '')
        crosswords.env.reset()
        loc = dfs(llm, nodes)
        end_time = time.time()
        loc['id'] = parameters.idx
        loc['cost time'] = end_time - start_time
        locs.append(loc)
        print(loc)
        crosswords.env.reset()
        parameters.increase_idx()
    record.Record_json(parameters.json_file_name, locs)