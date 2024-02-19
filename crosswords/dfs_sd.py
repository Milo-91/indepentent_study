import record_function as record
import parameters
import crosswords_function as crosswords
import tree_graph

# global variables
steps = list()
all_nodes = list()
d_thres = 0


def __dfs__(llm, node, best_node, max_value, graph, distance, sd = False):
    record.Record_txt(parameters.file_name, '\nO  now step: ' + str(crosswords.env.t) + '\nboard:\n' + crosswords.env.board_render() + '\nstatus:\n' + str(crosswords.env.status) + '\n\n')
    global d_thres
    # if achieving leaf node
    if crosswords.env.t == parameters.T or crosswords.env.board_complete():
        # save result and then back
        score = crosswords.Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])
        # simple dfs
        is_best = False
        if score > max_value:
            best_node = node.copy()
            max_value = score
            is_best = True
            # dfs with sphere decoding
            global d_thres
            d_thres = 30 - max_value
        steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'is_best': is_best, 'is_back': False, 'selected_node': node})
        
        return best_node, max_value

    parent = node['id']
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
        graph.add_nodes(new_nodes)
    
    # use graph to traversal
    input = graph.tree_head[parent]['next_node']
    while input['node'] != None:
        input_node = input['node']
        # if distance > d_thres -> prune
        distance += 10 - crosswords.Value_mapping(input_node['value'])
        board = crosswords.env.board.copy()
        status = crosswords.env.status.copy()
        t = crosswords.env.t
        if distance < d_thres:    
            # put input_node into next step
            steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'is_best': False, 'is_back': False, 'selected_node': input_node})
            crosswords.env.change_env(input_node['answer'])
            record.Record_txt(parameters.file_name, '\nselected node:\n' + str(input_node) + '\n\n')
            best_node, max_value = __dfs__(llm, input_node, best_node, max_value, graph, distance, sd = sd)
            if crosswords.env.t != parameters.T and crosswords.env.board_complete():
                crosswords.env.reset(board = board, status = status, t = t, id = crosswords.env.id)
        else:
            steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'is_best': False, 'is_back': True, 'selected_node': input_node})

        distance -= 10 - crosswords.Value_mapping(input_node['value'])
        # linked list connect to next node
        input = input['next_node']
    
    return best_node, max_value

def dfs(llm, node, sd = False):
    global d_thres, all_nodes, steps
    # initialize
    # reset all_nodes & steps
    all_nodes = list()
    steps = list()
    graph = tree_graph.graph()
    max_value = 0
    best_node = None
    all_nodes.append(node[0].copy())
    
    best_node, max_value = __dfs__(llm, node[0], best_node, max_value, graph, 0, sd = sd)

    record.Record_txt(parameters.file_name, '\n-----algorithm complete-----\n\n')
    
    graph.show_in_linked_list()
    
    answer = crosswords.env.board.copy()
    loc = {'id': None, 'steps': steps, 'answer': answer, 'correct': None}
    return loc