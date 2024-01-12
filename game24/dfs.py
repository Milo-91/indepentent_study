import game24_functions as game24
import parameters
import record_function as record
import datetime


steps = list()
all_nodes = list()

def __dfs__(llm, node, best_node, max_value):
    record.Record_txt(parameters.file_name, f'\nstep {parameters.t}\n\n')
    # if achieving leaf node
    if parameters.t == parameters.T:
        # save result and then back
        score = game24.Value_mapping(node['value']) + (0 if node['ancestor_value'] == None else node['ancestor_value'])
        is_best = False
        if score > max_value:
            print('max')
            best_node = node.copy()
            max_value = score
            is_best = True
        steps.append({'step': parameters.t, 'nodes': all_nodes.copy(), 'is_best': is_best})
        parameters.decrease_t()
        return best_node, max_value

    # Generator
    new_nodes = game24.Generator(llm, [node])
    # Evaluator
    new_nodes = game24.Evaluator(llm, new_nodes)
    # record
    record.Record_txt(parameters.file_name, '\nnode:\n' + str(new_nodes) + '\n' + str(len(new_nodes)) + '\n\n')
    all_nodes.extend(new_nodes)
    for new_node in new_nodes:
        # put new_nodes into next step
        record.Record_txt(parameters.file_name, '\ninput_node:' + str(new_node) + '\n\n')
        parameters.increase_t()
        print(f't: {parameters.t}, new_node: {new_node}')
        best_node, max_value = __dfs__(llm, new_node, best_node, max_value)
    
    parameters.decrease_t()
    return best_node, max_value

def dfs(llm, node):
    # initialize
    max_value = 0
    best_node = None
    all_nodes.append(node[0].copy())
    best_node, max_value = __dfs__(llm, node[0], best_node, max_value)
    print(all_nodes)
    record.Record_txt(parameters.file_name, '\nall_nodes:\n' + '\n'.join(list(map(str, all_nodes.copy()))) + '\n\n')

    # generate a final answer
    best = best_node
    path = list()
    while best['parent_node'] != None:
        path.append(best['answer'])
        best = all_nodes[best['parent_node']]
    path.append('(left: ' + all_nodes[0]['answer'] + ')')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    answer = game24.Final_Generator(llm, path)
    record.Record_txt(parameters.file_name, '\nAnswer: \n' + answer + '\n\n')
    
    loc = {'id': None, 'steps': steps, 'answer': answer, 'correct': None}
    print(f'loc: {loc}')
    return loc


