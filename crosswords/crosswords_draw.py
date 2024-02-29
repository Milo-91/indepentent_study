import json
import graphviz
import os
import parameters
import matplotlib.pyplot as plt
import re
import crosswords_function as crosswords
os.environ["PATH"] += os.pathsep + 'C:/FreeSpace/Graphviz/bin'


def Draw(file_name):
    with open(file_name, 'r', encoding="utf-8") as file:
        data = json.load(file)
    
    for i in range(len(data)):
        dot = graphviz.Digraph(comment = 'tree_' + str(i), format = 'png')
        Final = data[i]['steps'][-1]['nodes']
        print(data[i]['id'])
        selected_nodes = set()
        for step in data[i]['steps']:
            selected_nodes.add(step['selected_node']['id'])
        best_nodes = set()
        for step in data[i]['steps']:
            if step['is_best'] == True:
                best_nodes.add(step['selected_node']['id'])
        for path in data[i]['path']:
            best_nodes.add(path)
        back_nodes = set()
        for step in data[i]['steps']:
            if step['is_back'] == True:
                back_nodes.add(step['selected_node']['id'])
        
        print(selected_nodes)
        print(Final)
        for node in Final:
            if node['id'] in best_nodes:
                dot.node(str(node['id']), str(node['id']) + '\n' + str(node['answer']) + '\nparent: ' + str(node['parent_node']) + '\nvalue: ' + str(node['value']), color = 'blue')
            elif node['id'] in back_nodes:
                dot.node(str(node['id']), str(node['id']) + '\n' + str(node['answer']) + '\nparent: ' + str(node['parent_node']) + '\nvalue: ' + str(node['value']), color = 'yellow')
            else:
                dot.node(str(node['id']), str(node['id']) + '\n' + str(node['answer']) + '\nparent: ' + str(node['parent_node']) + '\nvalue: ' + str(node['value']))
            if node['parent_node'] != None:
                dot.edge(str(node['parent_node']), str(node['id']), label = str(crosswords.distance_calculator(node['value'], (0 if node['ancestor_distance'] == None or node['ancestor_distance'] == -1 else node['ancestor_distance']))), fontsize = '32')
        
        if not os.path.exists(parameters.image_folder):
            os.makedirs(parameters.image_folder)
        output_path = os.path.join(parameters.image_folder, f'tree_{i}')
        dot.render(output_path, view = False)


def Draw_table(path):
    board = [['-' for _ in range(5)] for _ in range(5)]
    fig, ax = plt.subplots(5, 2, figsize = (6, 8))
    fig.patch.set_visible(False)
    count = 0
    for ans in path:
        blue_list = list()
        red_list = list()
        pattern = r'(\d+)\. (\w+)'
        match = re.match(pattern, ans)
        if match:
            idx = int(match.group(1)) - 1
            word = match.group(2)
        else:
            print('error format')
            break
        print(idx, word)
        if idx < 5:
            for i in range(5):
                # if overwriting board
                if board[idx][i] != '-' and board[idx][i] != word[i]:
                    red_list.append((idx, i))
                else:
                    blue_list.append((idx, i))
                board[idx][i] = word[i]
        else:
            for i in range(5):
                 # if overwriteing board
                if board[i][idx - 5] != '-' and board[i][idx - 5] != word[i]:
                    red_list.append((i, idx - 5))
                else:
                    blue_list.append((i, idx - 5))
                board[i][idx - 5] = word[i]

        ax[count % 5][count // 5].axis('off')
        table1 = ax[count % 5][count // 5].table(cellText = board, loc = 'center', cellLoc = 'center', colWidths = [0.2 for _ in range(5)], fontsize = 12)
        for pos in blue_list:
            table1.get_celld()[pos].set_facecolor("deepskyblue")
        for pos in red_list:
            table1.get_celld()[pos].set_facecolor("red")
        table1.scale(1, 1.3)
        count += 1
    
    output_path = os.path.join(parameters.image_folder, f'table_{parameters.idx}.png')
    plt.savefig(output_path)

if __name__ == '__main__':
    #Draw(parameters.all_json_file_name)
    Draw_table(['2. motor', '6. mound', '5. derid', '3. utopi', '1. matte', '10. erido', '8. tofer', '4. needy'])
