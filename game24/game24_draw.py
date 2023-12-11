import json
import graphviz


def Draw(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    
    for i in range(len(data)):
        dot = graphviz.Digraph(comment = 'tree_' + str(i), format = 'png')
        Final = data[0]['steps'][-1]['nodes']
        top_b = data[0]['steps'][-1]['top_b']
        for step in data[0]['steps']:
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
        
           
        dot.render(f'tree_{i}.gv', view = True)
