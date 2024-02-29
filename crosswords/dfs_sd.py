import record_function as record
import parameters
import crosswords_function as crosswords
import tree_graph
import crosswords_draw as draw
import acc

# global variables
steps = list()
all_nodes = list()
d_thres = 10000


def __dfs__(llm, node, best_node, min_error, best_board, graph, distance, sd = False):
    record.Record_txt(parameters.file_name, '\nO  now step: ' + str(crosswords.env.t) + '\nboard:\n' + crosswords.env.board_render() + '\nstatus:\n' + str(crosswords.env.status) + '\n\n')
    global d_thres
    # max id 100
    if crosswords.env.id >= parameters.max_steps:
        return best_node, min_error, best_board
    # if achieving leaf node
    if crosswords.env.t == parameters.T or crosswords.env.board_complete():
        # save result and then back
        error = crosswords.distance_calculator(node['value'], (0 if node['ancestor_distance'] == None or node['ancestor_distance'] == -1 else node['ancestor_distance']))
        # simple dfs
        is_best = False
        if error < min_error and crosswords.env.board_complete():
            best_node = node.copy()
            min_error = error
            best_board = crosswords.env.board.copy()
            is_best = True
            # dfs with sphere decoding
            if sd == True:
                d_thres = distance
            record.Record_txt(parameters.file_name, '\nchange min_error: ' + str(min_error) + '\n\n')
            record.Record_txt(parameters.file_name, 'change best board: ' + str(best_board.copy()) + 'acc: ' + str(acc.acc(best_board.copy(), parameters.idx)) + '\n\n')
        steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'is_best': is_best, 'is_back': False, 'selected_node': node})
        record.Record_txt(parameters.file_name, '\n-----find leaf node and return-----\n\n')
        return best_node, min_error, best_board

    parent = node['id']
    print(f'parent: {parent}, graph linked list: {graph.total_element}')
    graph.add_head_list_len(parent)
    print(f'total element: {graph.total_element}')
    if graph.tree_head[parent]['next_node']['node'] == None:
        # if has not visited yet
        # Generator
        new_nodes = crosswords.Generator(llm, node)
        # Evaluator
        new_nodes = crosswords.Evaluator(llm, new_nodes)
        new_nodes = sorted(new_nodes, key = crosswords.Sorted_by_value, reverse = True)
        # record
        if new_nodes != None:
            record.Record_txt(parameters.file_name, '\nnode:\n' + '\n'.join(list(map(str, new_nodes.copy()))) + '\nlen: ' + str(len(new_nodes)) + '\n\n')
        all_nodes.extend(new_nodes)
        all_nodes = sorted(all_nodes, key = crosswords.Sorted_by_id, reverse = False)
        graph.add_nodes(new_nodes)
    
    # use graph to traversal
    input = graph.tree_head[parent]['next_node']
    while input['node'] != None:
        input_node = input['node']
        # skip wrong answer
        if input['node']['answer'] == 'wrong answer':
            input = input['next_node']
            continue
        # if distance > d_thres -> prune
        distance_copy = distance
        distance = crosswords.distance_calculator(input_node['value'], (0 if input_node['ancestor_distance'] == None or input_node['ancestor_distance'] == -1 else input_node['ancestor_distance']))
        board = crosswords.env.board.copy()
        status = crosswords.env.status.copy()
        t = crosswords.env.t
        record.Record_txt(parameters.file_name, '\ndistance: ' + str(distance) + '\nd_thres: ' + str(d_thres) + '\n\n')
        if sd == True:
            if distance < d_thres and crosswords.env.id < parameters.max_steps:
                # put input_node into next step
                steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'is_best': False, 'is_back': False, 'selected_node': input_node})
                crosswords.env.change_env(input_node['answer'])
                record.Record_txt(parameters.file_name, '\nselected node:\n' + str(input_node) + '\n\n')
                best_node, min_error, best_board = __dfs__(llm, input_node, best_node, min_error, best_board, graph, distance, sd = sd)
                crosswords.env.reset(board = board, status = status, t = t, id = crosswords.env.id)
            else:
                steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'is_best': False, 'is_back': True if distance >= d_thres else False, 'selected_node': input_node})
                if distance >= d_thres:
                    record.Record_txt(parameters.file_name, '\nprune node ' + str(input_node) + ': ' + str(distance) + ' / ' + str(d_thres) + '\n\n')
                if crosswords.env.id >= parameters.max_steps:
                    record.Record_txt(parameters.file_name, '\nmax id ' + str(crosswords.env.id) + '\n\n')
        else:
            # put input_node into next step
            steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'is_best': False, 'is_back': False, 'selected_node': input_node})
            crosswords.env.change_env(input_node['answer'])
            record.Record_txt(parameters.file_name, '\nselected node:\n' + str(input_node) + '\n\n')
            best_node, min_error, best_board = __dfs__(llm, input_node, best_node, min_error, best_board, graph, distance, sd = sd)
            crosswords.env.reset(board = board, status = status, t = t, id = crosswords.env.id)
            record.Record_txt(parameters.file_name, '\nreset board:\n' + str(board) +  '\n\n')
            print('reset\n' + str(board))
        
        distance = distance_copy
        # linked list connect to next node
        input = input['next_node']

    record.Record_txt(parameters.file_name, '\n-----end one layer and return-----\n\n')
    return best_node, min_error, best_board

def dfs(llm, node, sd = False):
    global d_thres, all_nodes, steps
    # initialize
    # reset all_nodes & steps
    all_nodes = list()
    steps = list()
    graph = tree_graph.graph()
    min_error = d_thres
    best_node = None
    best_board = None
    all_nodes.append(node[0].copy())
    
    best_node, min_error, best_board = __dfs__(llm, node[0], best_node, min_error, best_board, graph, 0, sd = sd)

    record.Record_txt(parameters.file_name, '\n-----algorithm complete-----\n\n')
    record.Record_txt(parameters.file_name, '\nall nodes: ' + '\n'.join(list(map(str, all_nodes.copy()))) + '\n')

    graph.show_in_linked_list()
    # best path
    best = best_node
    path = list()
    path_id = list()
    record.Record_txt(parameters.file_name, '\nbest node: ' + str(best) + '\n')
    while best['parent_node'] != None:
        path = [best['answer']] + path
        path_id = [best['id']] + path_id
        best = all_nodes[best['parent_node']]
        record.Record_txt(parameters.file_name, '\nbest node: ' + str(best) + '\n')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    draw.Draw_table(path)
    
    loc = {'id': None, 'steps': steps, 'answer': best_board, 'path': path_id, 'correct': None}
    return loc