import tot.record_functions as record


class graph():
    # element {node: dict, prev node: dict, next node: dict}
    # node: {id, answer, value, parent_node, ancestor_distance}
    def __init__(self, k, idx):
        self.total_element = k**3 + k**2 + k + 1
        self.tree_head = self.init_tree_head()
        self.visited = [0] * (self.total_element)
        self.idx = idx

    def reset_idx(self, idx):
        self.idx = idx
    
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

    def append_tree_head(self, origin_tree_head):
        # need to adjust total_element before call this function
        tree_head = origin_tree_head
        new_len = self.total_element - len(origin_tree_head)
        for _ in range(new_len):
            new_node = {'node': None, 'prev_node': None, 'next_node': None}
            new_node['prev_node'] = new_node
            new_node['next_node'] = new_node
            tree_head.append(new_node)

        return tree_head

    def show_in_linked_list(self):
        count = 0
        record.Record_txt(record.record_file_name, '\nlinked list:\n', self.idx)
        for node in self.tree_head:
            print("{:03}".format(count), end = '')
            record.Record_txt(record.record_file_name, "{:03}".format(count), self.idx)
            while node['next_node']['node'] != None:
                record.Record_txt(record.record_file_name, ' -> ' + str(node['next_node']['node']['id']), self.idx)
                print(' -> ', end = '')
                print(node['next_node']['node']['id'], end = '')
                node = node['next_node']
            count += 1
            print('') # '\n'
            record.Record_txt(record.record_file_name, '\n\n', self.idx)

    def visit_nodes(self, nodes):
        for node in nodes:
            id = node['id']
            print('visited id: ' + str(id))
            self.visited[id] = 1

    def add_head_list_len(self, new_len):
        # adjust length of visited & total_element & tree_head
        if new_len >= self.total_element:
            record.Record_txt(record.record_file_name, '\nadjust graph list length ' + str(self.total_element), self.idx)
            self.visited.extend([0] * (new_len - self.total_element + 1))
            self.total_element = new_len + 1
            self.tree_head = self.append_tree_head(self.tree_head)
            record.Record_txt(record.record_file_name, ' -> ' + str(self.total_element) + '\n\n', self.idx)

    def show_in_nodes(self):
        for node in self.tree_head:
            while node['next_node']['node'] != None:
                record.Record_txt(record.record_file_name, str(node['next_node']['node']) + '\n', self.idx)
                print(node['next_node']['node'])
                node = node['next_node']
        record.Record_txt(record.record_file_name, '\n', self.idx)