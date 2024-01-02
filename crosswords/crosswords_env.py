import json
import parameters
import re

class CrosswordsEnv():
    def __init__(self, file_name):
        self.all_data = self.load_data(file_name)
        self.id = 0

    def get_id(self):
        self.id += 1
        return self.id - 1

    def load_data(self, file_name):
        data = None
        with open(file_name, 'r') as file:
            data = json.load(file)
        return data

    def reset(self, board = None, status = None, t = None, id = None):
        self.board = ['_'] * 25 # 25 blanks on the board
        self.ans = ['_____'] * 10 # memory each line
        self.status = [0] * 10 # 10 lines status 0: Unfilled, 1: Filled, 2: Changed
        self.t = 0 # steps
        self.id = 0
        self.data = self.all_data[parameters.idx][0]
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