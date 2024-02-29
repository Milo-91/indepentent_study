import crosswords_function as crosswords
from crosswords import *
import tree_graph
import record_function as record
import parameters
import crosswords_draw as draw
import acc


def ksd(llm, nodes, graph=None):
    # initialize
    steps = list()
    level_nodes = [[] for _ in range(parameters.T + 1)]
    if graph == None:
        graph = tree_graph.graph()
    root_node = nodes[0].copy()
    d_thres = 10000
    best_board = None
    min_error = d_thres

    print('b = ' + str(parameters.b))
    record.Record_txt(parameters.file_name, '\nb = ' + str(parameters.b) + '\n\n')
    for i in range(parameters.b):
        record.Record_txt(parameters.file_name, '\n----- ' + str(i + 1) + 'th times -----\n\n')
        distance = 0
        top_b = [root_node]
        while not crosswords.env.board_complete() and crosswords.env.t < parameters.T and crosswords.env.id < parameters.max_steps:
            if distance > d_thres:
                # prune
                record.Record_txt(parameters.file_name, '\n(prune)distance: ' + str(distance) + ', d_thres: ' + str(d_thres) + '\n\n')
                break
            print(top_b)
            graph.visit_nodes(top_b)
            record.Record_txt(parameters.file_name, '\nvisited list: \n' + str(graph.visited) + '\n\n')
            print(f't: {crosswords.env.t}')
            record.Record_txt(parameters.file_name, f'\nstep {crosswords.env.t + 1}\n\n')
            parent = top_b[0]['id']
            graph.add_head_list_len(parent)
            if graph.tree_head[parent]['next_node']['node'] == None:
                # Generator
                new_nodes = crosswords.Generator(llm, top_b[0])
                # Evaluator
                new_nodes = crosswords.Evaluator(llm, new_nodes)
                # record
                record.Record_txt(parameters.file_name, '\ncreate new nodes: \n' + '\n'.join(list(map(str, new_nodes.copy()))) + '\n\n')
                # sort nodes
                level_nodes[crosswords.env.t].extend(new_nodes.copy())
                level_nodes[crosswords.env.t] = sorted(level_nodes[crosswords.env.t], key = crosswords.Sorted_by_value, reverse = True)

                nodes.extend(new_nodes)
                # add new_nodes in graph
                graph.add_nodes(new_nodes)
            record.Record_txt(parameters.file_name, '\n(' + str(crosswords.env.t) + ')level nodes: \n' + '\n'.join(list(map(str, level_nodes[crosswords.env.t].copy()))) + '\n\n')
            record.Record_txt(parameters.file_name, '\nlevel_nodes:\n' + str(level_nodes.copy()) + '\n\n')
            count = 0
            print(graph.visited)
            print(level_nodes[crosswords.env.t][count]['id'])
            while graph.visited[level_nodes[crosswords.env.t][count]['id']] == 1:
                print(level_nodes[crosswords.env.t][count]['id'])
                count += 1
            top_b = [level_nodes[crosswords.env.t][count]]
            record.Record_txt(parameters.file_name, '\nselected node: ' + str(top_b[0].copy()) + '\n\n')
            # change board to selected node status
            crosswords.env.reset(board = top_b[0]['board'], status = top_b[0]['status'], t = crosswords.env.t, id = crosswords.env.id)

            nodes = sorted(nodes, key = crosswords.Sorted_by_id)
            step = {'step': crosswords.env.t, 'nodes': nodes.copy(), 'top_b': top_b}
            if graph != None: # Greedy
                step['is_best'] = False if crosswords.env.t != parameters.T - 1 else True
                step['is_back'] = False
                step['selected_node'] = top_b[0].copy()
            steps.append(step)
            distance = crosswords.distance_calculator(top_b[0]['value'], top_b[0]['ancestor_distance'])
            crosswords.env.change_env(top_b[0]['answer'])

        ans_nodes = top_b[0]
        graph.visit_nodes(top_b)
        error = crosswords.distance_calculator(ans_nodes['value'], ans_nodes['ancestor_distance'])
        if error < min_error and crosswords.env.board_complete():
            min_error = error
            best_node = ans_nodes
            best_board = crosswords.env.board.copy()
            d_thres = min_error
            record.Record_txt(parameters.file_name, '\nchange min_error: ' + str(min_error) + '\n\n')
            record.Record_txt(parameters.file_name, 'change best board: ' + str(best_board.copy()) + 'acc: ' + str(acc.acc(best_board.copy(), parameters.idx)) + '\n\n')
        crosswords.env.reset(id = crosswords.env.id)

    # ksd complete
    graph.show_in_linked_list()
    best = best_node
    graph.visit_nodes([best])
    # best path
    best = best_node
    path = list()
    path_id = list()
    record.Record_txt(parameters.file_name, '\nbest node: ' + str(best) + '\n')
    while best['parent_node'] != None:
        path = [best['answer']] + path
        path_id = [best['id']] + path_id
        best = nodes[best['parent_node']]
        record.Record_txt(parameters.file_name, '\nbest node: ' + str(best) + '\n')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    draw.Draw_table(path)
    loc = {'id': None, 'steps': steps, 'answer': best_board, 'path': path_id, 'correct': None}
    return loc