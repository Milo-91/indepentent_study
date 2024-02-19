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
    format = r'([hv][1-5])\. .*\: ([a-zA-Z]{5})'
    parsed_lines = list()
    for line in response.split('\n'):
        print( 'line: ' + line + '\n')
        match = re.match(format, line)
        if match:
            parts = [match.group(1), match.group(2)]
            parsed_lines.append(parts)
    return parsed_lines


def Generator(llm, node, refine = False):
    # initialize
    record.Record_txt(parameters.file_name, '\n' + '-'*5 + 'Generator' + '-'*5 + '\n')
    confidence_to_value = {'certain': 1, 'high': 0.5, 'medium': 0.2, 'low': 0.1}
    new_nodes = list()
    # call llm
    input_string = env.board_render() + env.ans_render()
    question = propose_prompt.format(input = input_string, k = parameters.k)
    print('\nquestion:\n' +  question)
    record.Record_txt(parameters.file_name, '\nGenerator question: \n' + question + '\n\n')
    pattern = r'([hv][1-5])\. .*\: ([a-zA-Z]{5})'
    patterns = '\n'.join([pattern for i in range(parameters.k)])
    start_time = time.time()
    response = llm_function.call_llm(llm, question, patterns, parameters.generator_temperature)
    end_time = time.time()
    print('\nresponse:\n' + response)
    record.Record_txt(parameters.file_name, '\nGenerator response: \n' + response + '\n\n')
    # parse response & return 
    parsed_lines = Parse_propose_response(response)
    parsed_lines = [line[0].lower() + '. ' + line[1].lower()for line in parsed_lines]
    print('\nparsed lines:\n')
    print(parsed_lines)
    for i in range(len(parsed_lines)):
        if i == parameters.k:
            break
        new_nodes.append({'id': env.get_id(), 'answer': parsed_lines[i], 'value': None, 'parent_node': node['id'], 'ancestor_value': Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])})
    # add worng answer
    if len(parsed_lines) < parameters.k:
        new_nodes.extend([{'id': env.get_id(), 'answer': 'wrong answer', 'value': None, 'parent_node': None, 'ancestor_value': None} for _ in range(parameters.k - len(parsed_lines))])

    # refine
    '''
    if len(new_nodes) == 0:
        print('refine')
        new_nodes = Generator(llm, node, refine = True)
    '''
    if refine == False:
        print(f'cost time: {end_time - start_time}')
        record.Record_txt(parameters.file_name, 'Generator nodes:\n' + '\n'.join(list(map(str, new_nodes.copy()))) + '\ncost time: ' + str(end_time - start_time) + '\n\n')
    else:
        print(f'refine\ncost time: {end_time - start_time}')
        record.Record_txt(parameters.file_name, 'refine\ncost time: ' + str(end_time - start_time) + '\n\n')

    record.Record_txt(parameters.file_name, '-'*10 + '\n\n')
    return new_nodes


def Parse_value_response(response):
    answer = response.strip().split('\n')[-1]
    format = r'[hv][1-5]\. ((?:sure)|(?:maybe)|(?:impossible))'
    match = re.match(format, answer)
    if match:
        return match.group(1)
    else:
        return None


def Evaluator(llm, nodes):
    record.Record_txt(parameters.file_name, '\n' + '-'*5 + 'Evaluator' + '-'*5 + '\n')
    new_nodes = list()
    for node in nodes:
        # initialize
        count = {'sure': 0, 'maybe': 0, 'impossible': 0}
        board = env.board.copy()
        status = env.status.copy()
        t = env.t
        # skip wrong answer
        if node['answer'] == 'wrong answer':
            continue
        env.change_env(node['answer'])
        for i in range(10):
            print(env.board_render())
            print(f'env.ans: {env.ans[i]}')
            # skip _____ & ____ answers
            if env.ans[i].count('_') >= 4:
                count['sure'] += 1
                continue
            ans = ' '.join(env.ans[i].lower())
            if i < 5:
                line = f'h{i + 1}. {env.data[i]}: {ans}'
            else:
                line = f'v{i - 4}. {env.data[i]}: {ans}'
            print('each ans: ' + line)
            question = value_prompt.format(input = line)
            pattern = r"[\w|\W]*((?:sure)|(?:likely)|(?:impossible))$"
            # call llm
            start_time = time.time()
            response = llm_function.call_llm(llm, question, pattern, parameters.evaluator_temperature)
            end_time = time.time()
            # parse response & return
            print(response)
            print(f'cost time: {end_time - start_time}')
            record.Record_txt(parameters.file_name, '\ninput: ' + line + '\nEvaluator response: ' + response + '\ncost time: ' + str(end_time - start_time) + '\n')
            answer = Parse_value_response(response)
            if answer != None:
                count[answer] += 1
        node['value'] = count
        record.Record_txt(parameters.file_name, '\nanswer: ' + str(node['answer']) + '\nCount: ' + str(node['value']) + '\n\n')
        new_nodes.append(node)
        env.reset(board = board, status = status, t = t, id = env.id)
    record.Record_txt(parameters.file_name, '-'*10 + '\n\n')
    return new_nodes


def Value_mapping(value):
    if value == None:
        return 0
    count = 0
    count += value['sure'] * 10 + value['maybe'] * 5 + value['impossible'] * 1
    return count


def Sorted_by_value(node):
    return Value_mapping(node['value']) + node['ancestor_value']


def Sorted_by_id(node):
    return node['id']
    

if __name__ == '__main__':
    board = '______________________________'
    status = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    env.reset()
    print(env.board_render() + env.ans_render())
    env.change_env('h1. agend')
    print(env.board_render() + env.ans_render())
    env.change_env('v1. amass')
    print(env.board_render() + env.ans_render())
    print(env.status)
    '''
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
    '''
