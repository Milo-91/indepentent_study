import json
import graphviz
import os
import parameters


def Draw(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    
    for i in range(len(data)):
        dot = graphviz.Digraph(comment = 'tree_' + str(i), format = 'png')
        Final = data[i]['steps'][-1]['nodes']
        top_b = data[i]['steps'][-1]['top_b']
        for step in data[i]['steps']:
            Nodes = step['nodes']
        
        answer_path = [top_b[0]]
        while answer_path[-1]['parent_node'] != None:
            answer_path.append(Final[answer_path[-1]['parent_node']])
        
        counting = 0
        for node in Final:
            if answer_path[-1 + counting]['id'] == node['id']:
                dot.node(str(node['id']), str(node['id']) + '\n' + node['answer'] + '\nparent: ' + str(node['parent_node']), color = 'red')
                if counting > (-1 * len(answer_path) + 1):
                    counting -= 1
            else:
                dot.node(str(node['id']), str(node['id']) + '\n' + node['answer'] + '\nparent: ' + str(node['parent_node']))
            
            if node['parent_node'] != None:
                dot.edge(str(node['parent_node']), str(node['id']))
        
        if not os.path.exists(parameters.image_folder):
            os.makedirs(parameters.image_folder)
        output_path = os.path.join(parameters.image_folder, f'tree_{i}')
        dot.render(output_path, view = False)
