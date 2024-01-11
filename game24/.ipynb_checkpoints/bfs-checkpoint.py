import game24_functions as game24
import parameters
import record_function as record
import datetime


def bfs(llm, nodes):
    steps = list()
    top_b = nodes.copy()
    record.Init_record_file(parameters.file_name, parameters.huggingface_model_path + '\ntemperature: ' + str(parameters.generator_temperature) + ', ' +  str(parameters.evaluator_temperature) + '\ndate: ' + str(datetime.date.today()) + '\n\n')
    record.Init_record_file(parameters.json_file_name, '')

    for t in range(parameters.T):
        record.Record_txt(parameters.file_name, f'\nstep {t + 1}\n\n')
        # Generator
        new_nodes = game24.Generator(llm, top_b)
        # Evaluator
        new_nodes = game24.Evaluator(llm, new_nodes, t)
        # sort nodes
        new_nodes = sorted(new_nodes, key = game24.Sorted_by_value, reverse = True)
        record.Record_txt(parameters.file_name, '\nnode:\n' + str(new_nodes) + '\n' + str(len(new_nodes)) + '\n\n')
        # choose top b as the next input nodes
        top_b = new_nodes[:parameters.b]
        nodes.extend(new_nodes)
        nodes = sorted(nodes, key = game24.Sorted_by_id)
        steps.append({'step': t, 'nodes': nodes.copy(), 'top_b': top_b})

    # generate a final answer
    best = top_b[0]
    print(best)
    path = list()
    while best['parent_node'] != None:
        path.append(best['answer'])
        best = nodes[best['parent_node']]
    path.append('(left: ' + nodes[0]['answer'] + ')')
    print('\npath: ' + str(path) + '\n')
    record.Record_txt(parameters.file_name, '\npath: ' + str(path) + '\n\n')
    answer = game24.Final_Generator(llm, path)
    record.Record_txt(parameters.file_name, '\nAnswer: \n' + answer + '\n\n')

    loc = {'id': None, 'steps': steps, 'answer': answer, 'correct': None}
    return loc



