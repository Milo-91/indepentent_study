import json
import graphviz
import os
import parameters
os.environ["PATH"] += os.pathsep + 'C:/FreeSpace/Graphviz/bin'


def Draw(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    
    for i in range(len(data)):
        dot = graphviz.Digraph(comment = 'tree_' + str(i), format = 'png')
        Final = data[i]['steps'][-1]['nodes']
        selected_nodes = set()
        for step in data[i]['steps']:
            selected_nodes.add(step['selected_node']['id'])
        
        print(selected_nodes)
        for node in Final:
            if node['id'] in selected_nodes:
                dot.node(str(node['id']), str(node['id']) + '\n' + str(node['answer']) + '\nparent: ' + str(node['parent_node']) + '\nvalue: ' + str(node['value']), color = 'red')
            else:
                dot.node(str(node['id']), str(node['id']) + '\n' + str(node['answer']) + '\nparent: ' + str(node['parent_node']) + '\nvalue: ' + str(node['value']))
            
            if node['parent_node'] != None:
                dot.edge(str(node['parent_node']), str(node['id']))
        
        if not os.path.exists(parameters.image_folder):
            os.makedirs(parameters.image_folder)
        output_path = os.path.join(parameters.image_folder, f'tree_{i}')
        dot.render(output_path, view = False)

if __name__ == '__main__':
    Draw(parameters.all_json_file_name)
