from crosswords import *
import json
import llm_function
import parameters
import re

class CrosswordsEnv():
    def __init__(self, nodes: dict, file_name):
        self.nodes = nodes
        self.data = self.load_data(file_name)
        self.idx = None
        self.id = 0

    def increase_id(self):
        self.id += 1

    def load_data(self, file_name):
        data = None
        with open(file_name, 'r') as file:
            data = json.load(file)
        return data

    def reset(self, idx, board = None, status = None, t = None):
        self.board = ['_'] * 25 # 25 blanks on the board
        self.ans = ['_____'] * 10 # memory each line
        self.status = [0] * 10 # 10 lines status 0: Unfilled, 1: Filled, 2: Changed
        self.t = 0 # steps
        self.idx = idx # question data index
        self.data = self.data[idx][0]
        if board != None:
            self.board = board
            self.ans = self.get_ans(self.board)
        if status != None:
            self.status = status
        if t != None:
            self.t = t

    def board_render(self):
        string = 'Current Board\n'
        for i in range(5):
            string += ''.join(self.board[i * 5 : (i + 1) * 5])
            string += '\n'
        return string

    def get_lines(self, status):
        lines = list()
        # horizontal
        for i in range(5):
            #print(self.data[i])
            if status == None or self.status[i] == status:
                lines.append(f'h{i + 1}. ' + self.data[i] + ': ' + ''.join(self.board[i * 5 : (i + 1) * 5]))
        # vertical
        for i in range(5):
            if status == None or self.status[i + 5] == status:
                lines.append(f'v{i + 1}. ' + self.data[i] + ': ' + ''.join(self.board[i::5]))
        return lines

    def get_ans(self, board):
        ans = [''] * 10
        for i in range(5):
            ans[i] = ''.join(board[i * 5 : (i + 1) * 5])
        for i in range(5):
            ans[i] = ''.join(board[i::5])
        return ans

    def ans_render(self):
        string = 'Unfilled:\n'
        string += '\n'.join(self.get_lines(status = 0))
        string += '\nFilled:\n'
        string += '\n'.join(self.get_lines(status = 1))
        string += '\nChanged:\n'
        string += '\n'.join(self.get_lines(status = 2))
        string += '\n'

        return string

    def change_env(self, ans):
        format = r'^([hv][1-5])\. ([a-zA-Z]{5}) \((certain|high|medium|low)\).*$'
        match = re.match(format, ans)
        line_index, answer, _ = match.group(1), match.group(2), match.group(3)
        l = line_index[1]
        direction = line_index[0]
        #ans
        if direction == 'h':
            self.ans[l] = ans
        if direction == 'v':
            self.ans[l + 5] = ans
        #status
        for i in range(10):
            if direction == 'h':
                if all(element == '_' for element in self.board[l * 5 : (l + 1) * 5]):
                    self.status[l] = 1
                else:
                    self.status[l] = 2
            if direction == 'v':
                if all(element == '_' for element in self.board[l::5]):
                    self.status[l + 5] = 1
                else:
                    self.status[l + 5] = 2
        # board
        if direction == 'h':
            self.board[l * 5 : (l + 1) * 5] = [char for char in answer]
        if direction == 'v':
            self.board[l::5] = [char for char in answer]
        # t
        self.t += 1


def Parse_propose_response(response: str):
    format = r'^([hv][1-5])\. ([a-zA-Z]{5}) \((certain|high|medium|low)\).*$'
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
    confidence_to_value = {'certian': 1, 'high': 0.5, 'medium': 0.2, 'low': 0.1}
    new_nodes = list()
    # call llm
    input_string = env.board_render() + env.ans_render()
    question = propose_prompt.format(input = input_string)
    print('\nquestion:\n' +  question + '\n')
    response = llm_function.call_llm(llm, question)
    print('\nresponse:\n' + response.choices[0].message.content + '\n')
    # parse response & return 
    parsed_lines = Parse_propose_response(response.choices[0].message.content + '\n')
    parsed_lines = [(line[0].lower() + '. ' + line[1].lower(), confidence_to_value.get(line[2], 0)) for line in parsed_lines]
    parsed_lines = sorted(parsed_lines, key = lambda x: x[1], reverse = True)   
    print('\nparsed lines:\n')
    print(parsed_lines)
    for i in range(len(parsed_lines)):
        if i == parameters.k:
            break
        new_nodes.append({'id': env.id, 'answer': parsed_lines[i][0], 'value': None, 'parent_node': node['id']})
        env.increase_id()
    # refine
    if len(new_nodes) == 0:
        new_nodes = Generator(llm, node)
    return new_nodes


def Parse_value_response(llm, response):
    answer = response.strip().split('\n')[-1]
    if (answer != 'sure') and (answer != 'maybe') and (answer != 'impossible'):
        return None
    return answer


def Evaluator(llm, nodes):
    for node in nodes:
        env.change_env(node['answer'])
        count = {'sure': 0, 'maybe': 0, 'impossible': 0}
        for i in range(10):
            if self.ans[i].count('_') >= 4:
                continue
            ans = ''.join(self.ans.lower())
            line = f'{self.data[i]}: {ans[i]}'
            question = value_prompt.format(input = line)
            response = llm_function.call_llm(llm, question)
            print(response.choices[0].message.content)
            answer = Parse_value_response(response.choices[0].message.content)
            if answer != None:
                count[answer] += 1
        node['value'] = count
        new_nodes.append(node)

    return new_nodes


if __name__ == '__main__':
    file_name = 'data/mini0505.json'
    nodes = [{}]
    env = CrosswordsEnv(nodes = nodes, file_name = file_name)
    board = '______________________________'
    status = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    env.reset(idx = 0, board = board)
    #print(env.board_render())
    #print(env.ans_render())
    node = {'id': 0}
    llm = llm_function.get_llm()
    new_nodes = Generator(llm, node)
    print(new_nodes)

