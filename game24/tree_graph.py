import parameters
import record_function as record


class graph():
    # element {node: dict, prev node: dict, next node: dict}
    def __init__(self):
        self.total_element = parameters.k**3 + parameters.k**2 + parameters.k + 1
        self.tree_head = self.init_tree_head()
        self.visited = [0] * (self.total_element)
    
    def init_tree_head(self):
        # {node: None, prev_node: self, next_node: self}
        tree_head = list()
        for _ in range(self.total_element):
            new_node = {'node': None, 'prev_node': None, 'next_node': None}
            new_node['prev_node'] = new_node
            new_node['next_node'] = new_node
            tree_head.append(new_node)
        
        return tree_head
       
    def add_nodes(self, new_nodes):
        # add in tail
        for new_node in new_nodes:
            parent = new_node['parent_node']
            new_element = {'node': new_node, 'prev_node': self.tree_head[parent]['prev_node'], 'next_node': self.tree_head[parent]}
            self.tree_head[parent]['prev_node']['next_node'] = new_element
            self.tree_head[parent]['prev_node'] = new_element

    def show_in_linked_list(self):
        count = 0
        record.Record_txt(parameters.file_name, '\nlinked list:\n')
        for node in self.tree_head:
            print("{:03}".format(count), end = '')
            record.Record_txt(parameters.file_name, "{:03}".format(count))
            while node['next_node']['node'] != None:
                record.Record_txt(parameters.file_name, ' -> ' + str(node['next_node']['node']['id']))
                print(' -> ', end = '')
                print(node['next_node']['node']['id'], end = '')
                node = node['next_node']
            count += 1
            print('')
            record.Record_txt(parameters.file_name, '\n\n')

    def visit_nodes(self, nodes):
        for node in nodes:
            id = node['id']
            self.visited[id] = 1


if __name__ == '__main__':
    tree = graph()
    print(tree.total_element)
    print(tree.tree_head)
    new_nodes = [{'id': 1, 'parent_node': 0}, {'id': 2, 'parent_node': 0}, {'id': 3, 'parent_node': 0}]
    tree.add_nodes(new_nodes)
    new_nodes = [{'id': 10, 'parent_node': 0}, {'id': 20, 'parent_node': 100}]
    tree.add_nodes(new_nodes)
    print(tree.tree_head[0])
    tree.show_in_linked_list()
