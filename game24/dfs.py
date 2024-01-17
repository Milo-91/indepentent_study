import game24_functions as game24
import parameters
import record_function as record
import datetime
import tree_graph
import bfs


# global variables
steps = list()
all_nodes = list()
d_thres = 0


def Greedy(llm, node, graph):
    global d_thres, all_nodes
    parameters.set_b(initial_b = 1)
    loc = bfs.bfs(llm, node, graph)
    best_node = loc['steps'][-1]['top_b'][0]
    max_value = loc['path_value']
    d_thres = 30 - loc['path_value']
    record.Record_txt(parameters.file_name, f'\nd_thres: {d_thres}\n')
    all_nodes = loc['steps'][-1]['nodes']
    steps.extend(loc['steps'])
    return best_node, max_value

def __dfs__(llm, node, best_node, max_value, graph, distance):
    global d_thres
    record.Record_txt(parameters.file_name, f'\nstep {parameters.t}\n\n')
    # if achieving leaf node
    if parameters.t == parameters.T:
        # save result and then back
        score = game24.Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])
        # simple dfs
        is_best = False
        if score > max_value:
            print('max')
            best_node = node.copy()
            max_value = score
            is_best = True
            # dfs with sphere decoding
            global d_thres
            d_thres = 30 - max_value
        steps.append({'step': parameters.t, 'nodes': all_nodes.copy(), 'is_best': is_best, 'is_back': False, 'selected_node': node})
        
        parameters.decrease_t()
        return best_node, max_value

    parent = node['id']
    if graph.tree_head[parent]['next_node']['node'] == None:
        # if has not visited yet
        # Generator
        new_nodes = game24.Generator(llm, [node])
        # Evaluator
        new_nodes = game24.Evaluator(llm, new_nodes)
        # record
        if new_nodes != None:
            record.Record_txt(parameters.file_name, '\nnode:\n' + str(new_nodes) + '\n' + str(len(new_nodes)) + '\n\n')
        all_nodes.extend(new_nodes)
        graph.add_nodes(new_nodes)
    
    # use graph to traversal
    input = graph.tree_head[parent]['next_node']
    while input['node'] != None:
        input_node = input['node']
        # if distance > d_thres -> prune
        distance += 10 - game24.Value_mapping(input_node['value'])
        record.Record_txt(parameters.file_name, '\ndistance: ' + str(distance) + '\nd_threshold: ' + str(d_thres) + '\n')
        if distance < d_thres:    
            # put input_node into next step
            record.Record_txt(parameters.file_name, '\ninput_node:' + str(input_node) + '\n\n')
            steps.append({'step': parameters.t, 'nodes': all_nodes.copy(), 'is_best': False, 'is_back': False, 'selected_node': input_node})
            parameters.increase_t()
            print(f't: {parameters.t}, new_node: {input_node}')
            print(f'distance: {distance}')
            best_node, max_value = __dfs__(llm, input_node, best_node, max_value, graph, distance)
        else:
            steps.append({'step': parameters.t, 'nodes': all_nodes.copy(), 'is_best': False, 'is_back': True, 'selected_node': input_node})
            record.Record_txt(parameters.file_name, '\n(prune)input_node:' + str(input_node) + '\n\n')

        distance -= 10 - game24.Value_mapping(input_node['value'])
        input = input['next_node']
    
    parameters.decrease_t()
    return best_node, max_value

def dfs(llm, node):
    global d_thres
    # initialize
    graph = tree_graph.graph()
    max_value = 0
    best_node = None
    all_nodes.append(node[0].copy())
    # Greedy to define d_thres
    best_node, max_value = Greedy(llm, node, graph)
    print(f'd_thres: {d_thres}')
    best_node, max_value = __dfs__(llm, node[0], best_node, max_value, graph, 0)
    print(all_nodes)
    record.Record_txt(parameters.file_name, '\nall_nodes:\n' + '\n'.join(list(map(str, all_nodes.copy()))) + '\n\n')

    graph.show_in_linked_list()
    # generate a final answer
    best = best_node
    path = list()
    record.Record_txt(parameters.file_name, '\nbest node: ' + str(best) + '\n')
    while best['parent_node'] != None:
        path.append(best['answer'])
        best = all_nodes[best['parent_node']]
        record.Record_txt(parameters.file_name, '\nbest node: ' + str(best) + '\n')
    path.append('( left: ' + all_nodes[0]['answer'] + ' )')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    answer = game24.Final_Generator(llm, path)
    record.Record_txt(parameters.file_name, '\nAnswer: \n' + answer + '\n\n')
    
    loc = {'id': None, 'steps': steps, 'answer': answer, 'correct': None}
    # print(f'loc: {loc}')
    return loc


