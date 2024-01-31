import game24_functions as game24
import parameters
import record_function as record
import datetime
import tree_graph


def bfs(llm, nodes, graph=None, level_nodes=None):
    steps = list()
    top_b = nodes.copy()
    if graph == None:
        graph = tree_graph.graph()

    for t in range(parameters.T):
        print(top_b)
        graph.visit_nodes(top_b)
        print(f't: {t}')
        record.Record_txt(parameters.file_name, f'\nstep {t + 1}\n\n')
        # Generator
        new_nodes = game24.Generator(llm, top_b)
        # Evaluator
        new_nodes = game24.Evaluator(llm, new_nodes)
        # sort nodes
        new_nodes = sorted(new_nodes, key = game24.Sorted_by_value, reverse = True)
        if level_nodes != None:
            print('level_nodes\n' + str(level_nodes))
            print(t)
            record.Record_txt(parameters.file_name, '\nnew_node:\n' + '\n'.join(list(map(str, new_nodes.copy()))) + '\n\n')
            (level_nodes[t]).extend(new_nodes.copy())
            record.Record_txt(parameters.file_name, '\n(' + str(t) + ')level_nodes:\n' + '\n'.join(list(map(str, level_nodes[t].copy()))) + '\n\n')
            record.Record_txt(parameters.file_name, '\nlevel_nodes:\n' + str(level_nodes.copy()) + '\n\n')
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
    graph.visit_nodes([best])
    print(best)
    # calculate best path value
    path_value = game24.Value_mapping(best['value']) + best['ancestor_value']
    # generate a final answer
    loc = {'id': None, 'steps': steps, 'answer': None, 'path_value': path_value, 'correct': None, 'best_node': best}
    path = list()
    while best['parent_node'] != None:
        path.append(best['answer'])
        best = nodes[best['parent_node']]
    path.append('( left: ' + nodes[0]['answer'] + ' )')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    answer = game24.Final_Generator(llm, path)
    record.Record_txt(parameters.file_name, '\nAnswer: \n' + answer + '\n\n')

    loc['answer'] = answer
    return loc

def ksd(llm, nodes, max_value, best_node, Greedy_steps, level_nodes, graph=None):
    steps = Greedy_steps.copy()
    if graph == None:
        graph = tree_graph.graph()
    root_node = nodes[0].copy()
    d_thres = 30 - max_value

    print('b = ' + str(parameters.b))
    record.Record_txt(parameters.file_name, '\nb = ' + str(parameters.b) + '\n\n')
    for _ in range(parameters.b - 1):
        distance = 0
        top_b = [root_node]
        for t in range(parameters.T):
            if distance > d_thres:
                # prune
                record.Record_txt(parameters.file_name, '\n(prune)distance: ' + str(distance) + ', d_thres: ' + str(d_thres) + '\n\n')
                break
            print(top_b)
            graph.visit_nodes(top_b)
            record.Record_txt(parameters.file_name, '\nvisited list: \n' + str(graph.visited) + '\n\n')
            print(f't: {t}')
            record.Record_txt(parameters.file_name, f'\nstep {t + 1}\n\n')
            parent = top_b[0]['id']
            if graph.tree_head[parent]['next_node']['node'] == None:
                # Generator
                new_nodes = game24.Generator(llm, top_b)
                # Evaluator
                new_nodes = game24.Evaluator(llm, new_nodes)
                # record
                record.Record_txt(parameters.file_name, '\ncreate new nodes: \n' + '\n'.join(list(map(str, new_nodes.copy()))) + '\n\n')
                # sort nodes
                level_nodes[t].extend(new_nodes.copy())
                level_nodes[t] = sorted(level_nodes[t], key = game24.Sorted_by_value, reverse = True)

                nodes.extend(new_nodes)
                # add new_nodes in graph
                graph.add_nodes(new_nodes)
            record.Record_txt(parameters.file_name, '\n(' + str(t) + ')level nodes: \n' + '\n'.join(list(map(str, level_nodes[t].copy()))) + '\n\n')
            record.Record_txt(parameters.file_name, '\nlevel_nodes:\n' + str(level_nodes.copy()) + '\n\n')
            count = 0
            print(graph.visited)
            print(level_nodes[t][count]['id'])
            while graph.visited[level_nodes[t][count]['id']] == 1:
                print(level_nodes[t][count]['id'])
                count += 1
            top_b = [level_nodes[t][count]]

            nodes = sorted(nodes, key = game24.Sorted_by_id)
            step = {'step': t, 'nodes': nodes.copy(), 'top_b': top_b}
            if graph != None: # Greedy
                step['is_best'] = False if t != parameters.T - 1 else True
                step['is_back'] = False
                step['selected_node'] = top_b[0].copy() 
            steps.append(step)
            distance += 10 - game24.Value_mapping(top_b[0]['value'])

        ans_nodes = top_b[0]
        value = game24.Value_mapping(ans_nodes['value']) + ans_nodes['ancestor_value']
        if value > max_value:
            max_value = value
            best_node = ans_nodes
            d_thres = 30 - max_value

    graph.show_in_linked_list()
    best = best_node
    graph.visit_nodes([best])
    print(best)
    # calculate best path value
    path_value = max_value
    # generate a final answer
    loc = {'id': None, 'steps': steps, 'answer': None, 'path_value': path_value, 'correct': None, 'best_node': best}
    path = list()
    while best['parent_node'] != None:
        path.append(best['answer'])
        best = nodes[best['parent_node']]
    path.append('( left: ' + nodes[0]['answer'] + ' )')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    answer = game24.Final_Generator(llm, path)
    if answer != None:
        record.Record_txt(parameters.file_name, '\nAnswer: \n' + answer + '\n\n')

    loc['answer'] = answer
    return loc

