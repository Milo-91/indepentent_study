from game24 import *
import parameters
import re
import record_function as record
import llm_function


def Parse_propose_response(question: str, response: str):
    # if format is wrong return "wrong format"
    '''
    answers = []
    output_list = response.strip().split('\n')
    output_list = [x for x in output_list if 'left:' in x] + ['worng answer' for x in output_list if 'left:' not in x]
    if len(output_list) < parameters.k:
        output_list.extend(['worng answer'] * (parameters.k - len(output_list)))
    for i in range(parameters.k):
        answers.append(output_list[i])
    '''
    answers = []
    output_list = response.strip().split('\n')
    # add (left: numbers)
    pattern = r"(-?[0-9\.]+)[\s]*([\+\-\*\/])[\s]*(-?[0-9\.]+)[\s]*=[\s]*(-?[0-9\.]+)[\s]*"
    for i in range(len(output_list)):
        input_string = question
        match = re.match(pattern, output_list[i])
        if match:
            print(match.group(1), match.group(3), match.group(4))
            x1 = match.group(1)
            x2 = match.group(3)
            y = match.group(4)
            check = re.search(re.compile(x1), input_string)
            if check:
                input_string = input_string.replace(x1, '', 1)
                # print('x1 found')
            check = re.search(re.compile(x2), input_string)
            if check:
                input_string = input_string.replace(x2, y, 1)
                # print('x2 found')
            input_string = input_string.strip()
            input_string = input_string.replace('  ', ' ')
            print(input_string)
            output_list[i] = output_list[i] + f' ( left: {input_string} )'
        else:
            print('wrong format')
            output_list[i] = 'wrong answer'

    if len(output_list) < parameters.k:
        output_list.extend(['wrong answer'] * (parameters.k - len(output_list)))
    for i in range(parameters.k):
        answers.append(output_list[i])
        
    record.Record_txt(parameters.file_name, '\nGenerated answers:\n' + str(answers) + '\n\n')
    return answers


def Generator(llm, nodes: dict):
    new_nodes = list()
    print('Generator: ')
    for node in nodes:
        question = node['answer']
        if question == 'wrong answer':
            continue
        if re.search('left.+', node['answer']) != None:
            question = re.search('left.+', node['answer']).group().replace('left: ', '').replace(')', '').strip()
        input_string = propose_prompt.format(input = question, k = parameters.k)
        print('input:\n' + input_string)
        
        pattern = r"-?[0-9\.]+[\+\-\*\/ ]*-?[0-9\.]+[\s]*=[\s]*-?[0-9\.]+"
        patterns = '\n'.join([pattern for i in range(parameters.k)])
        response = llm_function.call_llm(llm, input_string, patterns, parameters.generator_temperature)

        print('\ngenerator response: \n' + response + '\n')
        record.Record_txt(parameters.file_name, '\nGenerator response:\n' + response + '\n\n')
        answers = Parse_propose_response(question, response)

        for answer in answers:
            new_nodes.append({'id': parameters.id, 'answer': answer, 'value': None, 'parent_node': node['id'], 'ancestor_value': Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])})
            parameters.increase_id()
    return new_nodes


def Parse_value_response(response, input):
    #if can't parse return None
    pattern = fr"Output: ((?:sure)|(?:likely)|(?:impossible)) \({input}\)".format(input = input)
    answer = re.search(pattern, response)
    print(pattern)
    print(f'evaluator parse: {answer}')
    if answer:
        return answer.group(1)
    else:
        return None
    


def Evaluator(llm, nodes: dict):
    new_nodes = list()
    for node in nodes:
        if node['answer'] == 'wrong answer':
            new_nodes.append(node)
            continue
        propose_response = node['answer']
        if re.search('left.+', node['answer']) != None:
            propose_response = re.search('left.+', node['answer']).group().replace('left: ', '').replace(')', '').strip()
        # propose_response += f' (len: {3 - t})'
        input_string = value_prompt.format(input = propose_response)
        print('input:\n' + input_string)

        # pattern = r"Analysis:[\w|\W]*[\n]Output: ((?:sure)|(?:likely)|(?:impossible))"
        pattern = None
        response = llm_function.call_llm(llm, input_string, pattern, parameters.evaluator_temperature)
        
        print('evaluator: \n' + response + '\n')
        record.Record_txt(parameters.file_name, '\n' + response + '\n\n')
        value = Parse_value_response(response, propose_response)

        node['value'] = value
        new_nodes.append(node)
    return new_nodes


def Parse_cot_answer(response):
    return response.strip().split('\n')[-1].lower().replace('answer: ', '').split('=')[0]


def Final_Generator(llm, path):
    '''
    input_string = cot_prompt.format(input = path)
    print(input_string)
    pattern = r"Answer: .*= 24"
    pattern_strickly = r"Answer:[\D]*([\d]+)[\D]*([\d]+)[\D]*([\d]+)[\D]*([\d]+)[\D]*= 24"
    response = llm_function.call_llm(llm, input_string, pattern_strickly)

    print('final answer: ' + response)
    answer = Parse_cot_answer(response)
    record.Record_txt(parameters.file_name, '\n' + response + '\n\n')
    '''
    left = None
    for i in range(3):
        match = re.search(r'(.+)[\s]*=[\s]*(-?[\d.]+)[\s]*\( left:(.+)\)', path[i])
        check = re.search(r'\( left:(.+)\)', path[i + 1]).group(1)
        if match:
            x = ' ( ' + match.group(1).strip() + ' ) ' # not replace ' ' to '' (negative numbers problem)
            y = match.group(2)
            y = ' ' + y + ' '
            print(x, y)
            if left == None:
                left = match.group(3)
        else:
            print("cant match path format")
            # record.Record_txt(parameters.file_name, '\nwrong path format\n' + str(path) + '\n\n')
            break

        left = left.replace(y, x, 1)
        print(sorted(re.findall(r'-?\d+', left), key = lambda x: int(x)))
        print(sorted(re.findall(r'-?\d+', check),  key = lambda x: int(x)))
        if sorted(re.findall(r'-?\d+', left), key = lambda x: int(x)) == sorted(re.findall(r'-?\d+', check),  key = lambda x: int(x)):
            print('correct foramt')
        else:
            print('wrong format')
            print(f'match: {match}')
            print(f'check: {check}')
            record.Record_txt(parameters.file_name, '\nwrong format\n' + left + '\n' + check + '\n\n')
            break
    if path != None and left != None:
        record.Record_txt(parameters.file_name, '\n' + str(path) + '\n' + left + '\n\n')
    return left


def Value_mapping(value):
    # sure 10, likely 5, impossible 1
    order = {'sure': 10, 'likely': 5, 'impossible': 1, '0': 0}
    return order.get(value, float(0))


def Sorted_by_value(node):
    return Value_mapping(node['value']) + node['ancestor_value']

def Sorted_by_id(node):
    return node['id']
