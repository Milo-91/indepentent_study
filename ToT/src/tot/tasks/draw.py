import graphviz
import os
import json

image_folder = 'logs/game24/record/image'

# use tree_graph to draw
def dfs_Draw(task, args, infos, graph, idx):
    dot = graphviz.Digraph(comment = 'tree_' + str(idx), format = 'png')
    # json file
    best_nodes = set()
    back_nodes = set()
    steps = infos
    for step in steps:
        if step['is_best'] == True:
            best_nodes.add(step['select_id'])
        if step['is_back'] == True:
            back_nodes.add(step['select_id'])
    # graph
    dot.node('0', '0' + '\n' + task.get_input(idx))
    for node in graph.tree_head:
        while node['next_node']['node'] != None:
            now_node = node['next_node']['node']
            # draw nodes
            if now_node['id'] in best_nodes:
                dot.node(str(now_node['id']), str(now_node['id']) + '\n' + str(now_node['answer'].split('\n')[-2]) + '\nparent: ' + str(now_node['parent_node']) + '\nvalue: ' + str(now_node['value']), color = 'blue')
            elif now_node['id'] in back_nodes:
                dot.node(str(now_node['id']), str(now_node['id']) + '\n' + str(now_node['answer'].split('\n')[-2]) + '\nparent: ' + str(now_node['parent_node']) + '\nvalue: ' + str(now_node['value']), color = 'yellow')
            else:
                dot.node(str(now_node['id']), str(now_node['id']) + '\n' + str(now_node['answer'].split('\n')[-2]) + '\nparent: ' + str(now_node['parent_node']) + '\nvalue: ' + str(now_node['value']))
            # draw edges
            if now_node['parent_node'] != None:
                dot.edge(str(now_node['parent_node']), str(now_node['id']), label = str(task.distance_calculator(now_node['value'], now_node['ancestor_distance'], args.n_evaluate_sample)), fontsize = '32')
            node = node['next_node']

    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    output_path = os.path.join(image_folder, f'tree_{idx}')
    dot.render(output_path, view = False)

