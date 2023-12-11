from game24 import *
import parameters
import re
import record_function as record
import llm_function


def Parse_propose_response(response: str):
    # if format is wrong return "wrong format"
    answers = []
    output_list = response.strip().split('\n')
    output_list = [x for x in output_list if 'left:' in x] + ['worng answer' for x in output_list if 'left:' not in x]
    if len(output_list) < parameters.k:
        output_list.extend(['worng answer'] * (parameters.k - len(output_list)))
    for i in range(parameters.k):
        answers.append(output_list[i])
    
    return answers


def Generator(llm, nodes: dict):
    new_nodes = list()
    print('Generator: ')
    for node in nodes:
        question = node['answer']
        if re.search('left.+', node['answer']) != None:
            question = re.search('left.+', node['answer']).group().replace('left: ', '').replace(')', '')
        input_string = propose_prompt.format(input = question, k = parameters.k)
        print('input:\n' + input_string)
        response = llm_function.call_llm(llm, input_string)
        #print('\ngenerator response: \n' + response['choices'][0]['text'] + '\n')
        #record.Record_txt(parameters.file_name, response['choices'][0]['text'] + '\n')
        #answers = Parse_propose_response(response['choices'][0]['text'])
        print('\ngenerator response: \n' + response.choices[0].message.content + '\n')
        record.Record_txt(parameters.file_name, response.choices[0].message.content + '\n')
        answers = Parse_propose_response(response.choices[0].message.content)
        for answer in answers:
            new_nodes.append({'id': parameters.id, 'answer': answer, 'value': None, 'parent_node': node['id'], 'ancestor_value': Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])})
            parameters.increase_id()
    return new_nodes


def Parse_value_response(response):
    #if can't parse return None
    answer = response.strip().split('\n')[-1]
    if ('sure' not in answer) and ('likely' not in answer) and ('impossible' not in answer):
        answer = None
    return answer


def Evaluator(llm, nodes: dict):
    new_nodes = list()
    for node in nodes:
        if node['answer'] == 'wrong answer':
            continue
        propose_response = node['answer']
        if re.search('left.+', node['answer']) != None:
            propose_response = re.search('left.+', node['answer']).group().replace('left: ', '').replace(')', '')
        input_string = value_prompt.format(input = propose_response)
        response = llm_function.call_llm(llm, input_string)
        #print('evaluator: \n' + response['choices'][0]['text'] + '\n')
        #record.Record_txt(parameters.file_name, response['choices'][0]['text'])
        #value = Parse_value_response(response['choices'][0]['text'])
        print('evaluator: \n' + response.choices[0].message.content + '\n')
        record.Record_txt(parameters.file_name, response.choices[0].message.content)
        value = Parse_value_response(response.choices[0].message.content)
        node['value'] = value
        new_nodes.append(node)
    return new_nodes


def Parse_cot_answer(response):
    return response.strip().split('\n')[-1].lower().replace('answer: ', '').split('=')[0]


def Final_Generator(llm, path: str):
    input_string = cot_prompt.format(input = path)
    response = llm_function.call_llm(llm, input_string)
    #print('final answer: ' + response['choices'][0]['text'])
    #answer = Parse_cot_answer(response['choices'][0]['text'])
    #record.Record_txt(parameters.file_name, response['choices'][0]['text'])
    print('final answer: ' + response.choices[0].message.content)
    answer = Parse_cot_answer(response.choices[0].message.content)
    record.Record_txt(parameters.file_name, response.choices[0].message.content)
    return answer


def Value_mapping(value):
    order = {'sure': 20, 'likely': 1, 'impossible': 0.001, '0': 0}
    return order.get(value, float(0))


def Sorted_by_value(node):
    return Value_mapping(node['value']) + node['ancestor_value']
