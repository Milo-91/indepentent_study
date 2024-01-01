import crosswords_function as crosswords

env = crosswords.CrosswordsEnv()

def dfs(llm, nodes):
    for node in nodes:
        new_nodes = crosswords.Generator(llm, node)
        new_nodes = crosswords.Evaluator(llm, new_nodes)
        new_nodes = new_nodes = sorted(new_nodes, key = crosswords.Sorted_by_value)
        if new_nodes[0]['value']['impossible'] >= 1:
            # prune
            env.reset()
            continue
        else:
            dfs(llm, new_nodes)