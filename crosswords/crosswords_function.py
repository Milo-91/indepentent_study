from crosswords import *
import json
import llm_function
import parameters
import re
import record_function as record
import crosswords_env
import time

env = crosswords_env.CrosswordsEnv(file_name = parameters.data_path_crosswords)

def Parse_propose_response(response: str):
    format = r'^([hv][1-5])\. ([a-zA-Z]{5}) \((certain|high|medium|low)\)$'
    parsed_lines = list()
    for line in response.split('\n'):
        print( 'line: ' + line + '\n')
        match = re.match(format, line)
        if match:
            parts = [match.group(1), match.group(2), match.group(3)]
            parsed_lines.append(parts)
    return parsed_lines


def Generator(llm, node):
    # initialize
    confidence_to_value = {'certain': 1, 'high': 0.5, 'medium': 0.2, 'low': 0.1}
    new_nodes = list()
    env.change_env(node['answer']) # change env
    # call llm
    input_string = env.board_render() + env.ans_render()
    question = propose_prompt.format(input = input_string, k = parameters.k)
    print('\nquestion:\n' +  question + '\n')
    pattern = r'([hv][1-5])\. ([a-zA-Z]{5}) \((certain|high|medium|low)\)'
    patterns = '\n'.join([pattern for i in range(parameters.k)])
    start_time = time.time()
    response = llm_function.call_llm(llm, question, patterns)
    end_time = time.time()
    print('\nresponse:\n' + response + '\n')
    # parse response & return 
    parsed_lines = Parse_propose_response(response + '\n')
    parsed_lines = [(line[0].lower() + '. ' + line[1].lower(), confidence_to_value.get(line[2], 0)) for line in parsed_lines]
    parsed_lines = sorted(parsed_lines, key = lambda x: x[1], reverse = True)   
    print('\nparsed lines:\n')
    print(parsed_lines)
    record.Record_txt(parameters.file_name, '\nGenerator: \n' + str(parsed_lines) + '\n')
    for i in range(len(parsed_lines)):
        if i == parameters.k:
            break
        new_nodes.append({'id': env.get_id(), 'answer': parsed_lines[i][0], 'value': None, 'parent_node': node['id'], 'ancestor_value': Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])})
    # refine
    if len(new_nodes) == 0:
        new_nodes = Generator(llm, node)
    print(f'cost time: {end_time - start_time}')
    record.Record_txt(parameters.file_name, 'Generator nodes:\n' + str(new_nodes) + '\ncost time: ' + str(end_time - start_time) + '\n\n')
    return new_nodes


def Parse_value_response(response):
    answer = response.strip().split('\n')[-1]
    if (answer != 'sure') and (answer != 'maybe') and (answer != 'impossible'):
        return None
    return answer


def Evaluator(llm, nodes):
    new_nodes = list()
    for node in nodes:
        count = {'sure': 0, 'maybe': 0, 'impossible': 0}
        board = env.board.copy()
        status = env.status.copy()
        t = env.t
        env.change_env(node['answer'])
        for i in range(10):
            print(env.board_render())
            print(f'env.ans: {env.ans[i]}')
            if env.ans[i].count('_') >= 4:
                continue
            ans = ''.join(env.ans[i].lower())
            line = f'{env.data[i]}: {ans}'
            print('each ans: ' + line)
            question = value_prompt.format(input = line)
            pattern = r"[\d|\w|\s|\+|\-|\*|\/|\=|\(|\)|,|\.|\:|\"|\'|_|;|\!|\?]{0,500}[sure|maybe|impossible]"
            start_time = time.time()
            response = llm_function.call_llm(llm, question, pattern)
            end_time = time.time()
            print(response)
            print(f'cost time: {end_time - start_time}')
            record.Record_txt(parameters.file_name, '\nEvaluator response: ' + response + '\ncost time: ' + str(end_time - start_time) + '\n')
            answer = Parse_value_response(response)
            if answer != None:
                count[answer] += 1
        node['value'] = count
        record.Record_txt(parameters.file_name, '\nanswer: ' + str(node['answer']) + '\nCount: ' + str(node['value']) + '\n\n')
        new_nodes.append(node)
        env.reset(board = board, status = status, t = t, id = env.id)
    return new_nodes


def Value_mapping(value):
    if value == None:
        return 0
    count = 0
    count += value['sure'] * 20 + value['maybe'] + value['impossible'] * 0.001
    return count


def Sorted_by_value(node):
    return Value_mapping(node['value']) + node['ancestor_value']


def Sorted_by_id(node):
    return node['id']
    

if __name__ == '__main__':
    file_name = 'data/mini0505.json'
    nodes = [{}]
    env = CrosswordsEnv(file_name = file_name)
    board = '______________________________'
    status = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    env.reset()
    #print(env.board_render())
    #print(env.ans_render())
    node = {'id': env.get_id()}
    llm = llm_function.get_llm()
    env.change_env('h1. agend')
    new_nodes = Generator(llm, node)
    print(new_nodes)
    print(env.board_render())
    board = env.board.copy()
    status = env.status.copy()
    t = env.t
    new_nodes = Evaluator(llm, new_nodes)
    print(new_nodes)
    env.reset(board = board, status = status, t = t, id = env.id)
    print(env.board, env.status, env.t)