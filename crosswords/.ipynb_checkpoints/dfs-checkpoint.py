import crosswords_function as crosswords
import record_function as record
import parameters

def dfs(llm, nodes):
    steps = list()
    board = crosswords.env.board.copy()
    status = crosswords.env.status.copy()
    t = crosswords.env.t
    if crosswords.env.t < parameters.T:
        for node in nodes:
            new_nodes = crosswords.Generator(llm, node)
            new_nodes = crosswords.Evaluator(llm, new_nodes)
            new_nodes = sorted(new_nodes, key = crosswords.Sorted_by_value)
            if new_nodes[0]['value']['impossible'] < 1:
                # possible branch
                print('-'*10)
                print(f'now step = {crosswords.env.t}')
                print(crosswords.env.board_render())
                print(f'next node = {new_nodes[0]}')
                print('-'*10)
                nodes.extend(new_nodes.copy())
                nodes = sorted(nodes, key = crosswords.Sorted_by_id)
                steps.append({'step': crosswords.env.t, 'nodes': nodes.copy(), 'selected_node': new_nodes[0].copy()})
                record.Record_txt(parameters.file_name, '\nSteps: \n' + str(crosswords.env.t) + '\nNodes:\n' + str(new_nodes) + '\nSelected nodes:\n' + str(new_nodes[0]) + '\n\n')
                dfs(llm, new_nodes.copy())
                if crosswords.env.t == parameters.T:
                    break
            crosswords.env.reset(board = board, status = status, t = t, id = crosswords.env.id)
    answer = crosswords.env.board.copy()
    loc = {'id': None, 'steps': steps, 'answer': answer, 'correct': None}
    return loc