import crosswords_function as crosswords
import record_function as record
import parameters


steps = list()
all_nodes = list()
def dfs(llm, nodes):
    board = crosswords.env.board.copy()
    status = crosswords.env.status.copy()
    t = crosswords.env.t
    if '_' in crosswords.env.board and crosswords.env.t < parameters.T:
        for node in nodes:
            crosswords.env.change_env(node['answer'])
            if '_' not in crosswords.env.board:
                record.Record_txt(parameters.file_name, '\nnow step: ' + str(crosswords.env.t) + '\nboard:\n' + crosswords.env.board_render() + '\n\n')
                steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'selected_node': node, 'is_back': False})
                break
            new_nodes = crosswords.Generator(llm, node)
            new_nodes = crosswords.Evaluator(llm, new_nodes)
            new_nodes = sorted(new_nodes, key = crosswords.Sorted_by_value, reverse = True)
            all_nodes.extend(new_nodes)
            if crosswords.Value_mapping(new_nodes[0]['value']) >= 50:# change threshold
                # possible branches
                print('-'*10)
                print(f'now step = {crosswords.env.t}\n')
                print(crosswords.env.board_render())
                print(crosswords.env.ans_render())
                print(crosswords.env.status)
                print(f'next node = {new_nodes[0]}')
                print(f'value = {new_nodes[0]["value"]}')
                print('-'*10)
                record.Record_txt(parameters.file_name, '\nnow step: ' + str(crosswords.env.t) + '\nboard:\n' + crosswords.env.board_render() + '\n\n')
                steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'selected_node': node, 'is_back': False})
                print(f'nodes: {all_nodes}')
                print(f'new_nodes: {new_nodes}')
                record.Record_txt(parameters.file_name, '\nSteps: \n' + str(crosswords.env.t) + '\nNodes:\n' + str(all_nodes) + '\nSelected node:\n' + str(new_nodes[0]) + '\n\n')
                dfs(llm, new_nodes.copy())
                if '_' not in crosswords.env.board or crosswords.env.t == parameters.T:
                    break
            else:
                # prune
                print('\nimpossible way then back\n')
                print(f'now step = {crosswords.env.t}')
                print(crosswords.env.board_render())
                print(f'nodes: {nodes}')
                print(f'new_nodes: {new_nodes}')
                record.Record_txt(parameters.file_name, '\n(prune)\nSteps: ' + str(crosswords.env.t) + '\nNodes:\n' + str(all_nodes) + '\nSelected node:\n' + str(new_nodes[0]) + '\n\n')
                steps.append({'step': crosswords.env.t, 'nodes': all_nodes.copy(), 'selected_node': node, 'is_back': True})
            crosswords.env.reset(board = board, status = status, t = t, id = crosswords.env.id)
            print('\nafter reset\n' + crosswords.env.board_render() + '\n')
    answer = crosswords.env.board.copy()
    loc = {'id': None, 'steps': steps, 'answer': answer, 'correct': None}
    print(loc)
    return loc
    
