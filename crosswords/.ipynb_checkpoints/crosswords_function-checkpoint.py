from crosswords import *
import json
import llm_function
import parameters
import re

class CrosswordsEnv():
    def __init__(self, nodes: dict, file_name):
        self.nodes = nodes
        self.all_data = self.load_data(file_name)
        self.idx = None
        self.id = 0

    def get_id(self):
        self.id += 1
        return self.id - 1

    def load_data(self, file_name):
        data = None
        with open(file_name, 'r') as file:
            data = json.load(file)
        return data

    def reset(self, idx, board = None, status = None, t = None, id = None):
        self.board = ['_'] * 25 # 25 blanks on the board
        self.ans = ['_____'] * 10 # memory each line
        self.status = [0] * 10 # 10 lines status 0: Unfilled, 1: Filled, 2: Changed
        self.t = 0 # steps
        self.idx = idx # question data index
        self.id = 0
        self.data = self.all_data[idx][0]
        if board != None:
            self.board = board
            self.ans = self.get_ans(self.board)
        if status != None:
            self.status = status
        if t != None:
            self.t = t
        if id != None:
            self.id = id

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
            ans[i + 5] = ''.join(board[i::5])
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
        format = r'^([hv][1-5])\. ([a-zA-Z]{5}).*$'
        match = re.match(format, ans)
        line_index, answer = match.group(1), match.group(2)
        l = int(line_index[1]) - 1
        print(f'line_index = {l}')
        direction = line_index[0]
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
        #ans
        self.ans = self.get_ans(self.board)


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
    # call llm
    input_string = env.board_render() + env.ans_render()
    question = propose_prompt.format(input = input_string, k = parameters.k)
    print('\nquestion:\n' +  question + '\n')
    pattern = r'([hv][1-5])\. ([a-zA-Z]{5}) \((certain|high|medium|low)\)'
    patterns = '\n'.join([pattern for i in range(parameters.k)])
    response = llm_function.call_llm(llm, question, patterns)
    print('\nresponse:\n' + response + '\n')
    # parse response & return 
    parsed_lines = Parse_propose_response(response + '\n')
    parsed_lines = [(line[0].lower() + '. ' + line[1].lower(), confidence_to_value.get(line[2], 0)) for line in parsed_lines]
    parsed_lines = sorted(parsed_lines, key = lambda x: x[1], reverse = True)   
    print('\nparsed lines:\n')
    print(parsed_lines)
    for i in range(len(parsed_lines)):
        if i == parameters.k:
            break
        new_nodes.append({'id': env.get_id(), 'answer': parsed_lines[i][0], 'value': None, 'parent_node': node['id']})
    # refine
    if len(new_nodes) == 0:
        new_nodes = Generator(llm, node)
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
        print(env.board_render())
        for i in range(10):
            print(f'env.ans: {env.ans[i]}')
            if env.ans[i].count('_') >= 4:
                continue
            ans = ''.join(env.ans[i].lower())
            line = f'{env.data[i]}: {ans}'
            print('each ans: ' + line)
            question = value_prompt.format(input = line)
            pattern = r"[\d|\w|\s|\+|\-|\*|\/|\=|\(|\)|,|\.|\:|\"|\'|_|;|\!|\?]{0,500}[sure|maybe|impossible]"
            response = llm_function.call_llm(llm, question, pattern)
            print(response)
            answer = Parse_value_response(response)
            if answer != None:
                count[answer] += 1
        node['value'] = count
        new_nodes.append(node)
        env.reset(idx = env.idx, board = board, status = status, t = t, id = env.id)
    return new_nodes


if __name__ == '__main__':
    file_name = 'data/mini0505.json'
    nodes = [{}]
    env = CrosswordsEnv(nodes = nodes, file_name = file_name)
    board = '______________________________'
    status = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    env.reset(idx = 0)
    #print(env.board_render())
    #print(env.ans_render())
    node = {'id': env.get_id()}
    llm = llm_function.get_llm()
    new_nodes = Generator(llm, node)
    print(new_nodes)
    # env.change_env(new_nodes[0]['answer'])
    print(env.board_render())
    board = env.board
    status = env.status
    t = env.t
    new_nodes = Evaluator(llm, new_nodes)
    print(new_nodes)
    env.reset(idx = env.idx, board = board, status = status, t = t, id = env.id)