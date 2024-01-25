import game24_functions as game24
import parameters
import record_function as record
import datetime
import tree_graph


def bfs(llm, nodes, graph=None):
    steps = list()
    top_b = nodes.copy()
    if graph == None:
        graph = tree_graph.graph()

    print('here')

    for t in range(parameters.T):
        print(f't: {t}')
        record.Record_txt(parameters.file_name, f'\nstep {t + 1}\n\n')
        # Generator
        new_nodes = game24.Generator(llm, top_b)
        # Evaluator
        new_nodes = game24.Evaluator(llm, new_nodes)
        # sort nodes
        new_nodes = sorted(new_nodes, key = game24.Sorted_by_value, reverse = True)
        record.Record_txt(parameters.file_name, '\nnode:\n' + str(new_nodes) + '\n' + str(len(new_nodes)) + '\n\n')
        # choose top b as the next input nodes
        top_b = new_nodes[:parameters.b]
        nodes.extend(new_nodes)
        # add new_nodes in graph
        graph.add_nodes(new_nodes)
        nodes = sorted(nodes, key = game24.Sorted_by_id)
        step = {'step': t, 'nodes': nodes.copy(), 'top_b': top_b}
        if graph != None: # Greedy
            step['is_best'] = False if t != parameters.T - 1 else True
            step['is_back'] = False
            step['selected_node'] = top_b[0].copy() 
        steps.append(step)


    graph.show_in_linked_list()
    best = top_b[0]
    print(best)
    # calculate best path value
    path_value = game24.Value_mapping(best['value']) + best['ancestor_value']
    # generate a final answer
    path = list()
    while best['parent_node'] != None:
        path.append(best['answer'])
        best = nodes[best['parent_node']]
    path.append('( left: ' + nodes[0]['answer'] + ' )')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    answer = game24.Final_Generator(llm, path)
    record.Record_txt(parameters.file_name, '\nAnswer: \n' + answer + '\n\n')

    loc = {'id': None, 'steps': steps, 'answer': answer, 'path_value': path_value, 'correct': None}
    return loc



