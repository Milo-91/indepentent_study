import pandas as pd
import json
import parameters
import llm_function
from bfs import *


if __name__ == '__main__':
    data_game24 = pd.read_csv('24.csv')
    llm = llm_function.get_llm()

    for i in range(1):
        nodes = [{'id': 0, 'answer': data_game24['Puzzles'][i], 'value': None, 'parent_node': None, 'ancestor_value': None}]
        answer = bfs(llm, nodes)
        print(answer)
