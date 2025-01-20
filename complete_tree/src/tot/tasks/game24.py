import re
import os
import sympy
import pandas as pd
from tot.tasks.base import Task, DATA_PATH
from tot.prompts.game24 import * 


def get_current_numbers(y: str) -> str:
    last_line = y.strip().split('\n')[-1]
    return last_line.split('left: ')[-1].split(')')[0].strip()


class Game24Task(Task):
    """
    Input (x)   : a string of 4 numbers
    Output (y)  : a trajectory of 3 steps to reach 24
    Reward (r)  : 0 or 1, depending on whether the trajectory is correct
    Input Example: 
        1 2 3 4
    Output Example: 
        1 + 2 = 3 (left: 3 3 4)
        3 + 3 = 6 (left: 4 6)
        6 * 4 = 24 (left: 24)
        (1 + 2 + 3) * 4 = 24
    """
    def __init__(self, file='24.csv'):
        """
        file: a csv file (fixed)
        """
        super().__init__()
        path = os.path.join(DATA_PATH, '24', file)
        self.data = list(pd.read_csv(path)['Puzzles'])
        self.value_cache = {}
        self.steps = 4
        self.stops = ['\n'] * 4
        self.id = 0

    def __len__(self) -> int:
        return len(self.data)
    
    def get_input(self, idx: int) -> str:
        return self.data[idx]

    def test_output(self, idx: int, output: str):
        expression = output.strip().split('\n')[-1].lower().replace('answer: ', '').split('=')[0]
        numbers = re.findall(r'\d+', expression)
        problem_numbers = re.findall(r'\d+', self.data[idx])
        if sorted(numbers) != sorted(problem_numbers):
            return {'r': 0}
        try:
            # print(sympy.simplify(expression))
            return {'r': int(sympy.simplify(expression) == 24)}
        except Exception as e:
            # print(e)
            return {'r': 0}
    
    def get_id(self):
        self.id += 1
        return self.id - 1
    
    def reset_id(self, id = None):
        if id == None:
            self.id = 0
        else:
            self.id = id
            
    @staticmethod
    def standard_prompt_wrap(x: str, y:str='') -> str:
        return standard_prompt.format(input=x) + y

    @staticmethod
    def cot_prompt_wrap(x: str, y:str='') -> str:
        return cot_prompt.format(input=x) + y
    
    @staticmethod
    def propose_prompt_wrap(x: str, y: str='', k: int = 1) -> str:
        current_numbers = get_current_numbers(y if y else x)
        if current_numbers == '24':
            prompt = cot_prompt.format(input=x) + 'Steps:' + y
            # print([prompt])
        else:
            prompt = propose_prompt.format(input=current_numbers, k=k)
        return prompt
    
    @staticmethod
    def value_prompt_wrap(y: str) -> str:
        last_line = y.strip().split('\n')[-1]
        # temp pass value_last_step
        '''
        if 'left: ' not in last_line:  # last step
            ans = last_line.lower().replace('answer: ', '')
            # print([value_last_step_prompt.format(input=x, answer=ans)])
            return value_last_step_prompt.format(input=x, answer=ans)
        '''
        current_numbers = get_current_numbers(y)
        return value_prompt.format(input=current_numbers)
    
    def __name_check__(self, name):
        validate_name = ['sure', 'likely', 'impossible']
        return name in validate_name
    
    @staticmethod
    def value_outputs_unwrap(y: str, value_outputs: list, evaluator_method, avg_probs: list = None) -> float:
        if len(y.strip().split('\n')) == 4 and 'answer' not in y.lower():
            return 0
        value_names = [_.split('\n')[-1] for _ in value_outputs]
        value_map = {'impossible': 0.001, 'likely': 1, 'sure': 20}  # TODO: ad hoc
        if evaluator_method == 'origin':
            value = sum(value * value_names.count(name) for name, value in value_map.items())
        elif evaluator_method == 'logprob':
            mix = list(zip(value_names, avg_probs))
            value = round(sum([prob * value_map[name] if name in value_map.keys() else 0 for name, prob in mix]) / sum(avg_probs), 3)
        return value
    
    @staticmethod
    def distance_calculator(value, ancestor_distance, n_evaluate_sample, evaluator_method):
        value_map = {'impossible': 0.001, 'likely': 1, 'sure': 20}
        max = value_map['sure']
        if value == None:
            return -1
        # maximum is sure * n_evaluate_sample
        if evaluator_method == 'origin':
            distance = max * n_evaluate_sample - value
        # maximum is sure
        elif evaluator_method == 'logprob':
            distance = max - value
        distance += ancestor_distance
        return distance