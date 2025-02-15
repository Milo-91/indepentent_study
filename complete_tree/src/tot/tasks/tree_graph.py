import tot.record_functions as record
import jsonpickle
import json
import sys

graph_json_file_name = 'logs/game24/record/graph_{idx}.json'

class graph():
    # element: {node: dict, prev node: dict, next node: dict}
    # nodes: {'0': node0, '1': node1, ...}
    # node: {id, answer, value, parent_node, ancestor_distance, generation cost time, evaluation cost time}
    def __init__(self, k, b, idx):
        self.total_element = k**3 + k**2 + k + 10
        self.tree_head = self.init_tree_head()
        self.nodes = dict()
        self.visited = [0] * (self.total_element)
        self.idx = idx

    def __copy__(self):
        new_instance = graph(0, 0, self.idx)
        new_instance.total_element = self.total_element
        new_instance.tree_head = self.tree_head.copy()
        new_instance.nodes = self.nodes.copy()
        new_instance.visited = self.visited.copy()
        
        return new_instance
    
    def __load_from_json__(self, file_path, idx):
        with open(file_path, 'r') as file:
            string = file.read()
            print(string)
        data = jsonpickle.decode(string)[idx]
        print(data)
        self.total_element = data['total_element']
        self.tree_head = data['tree_head']
        self.nodes = data['nodes']
        self.visited = data['visited']
        self.idx = data['idx']
    
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
            if parent != None:
                new_element = {'node': new_node, 'prev_node': self.tree_head[parent]['prev_node'], 'next_node': self.tree_head[parent]}
                self.tree_head[parent]['prev_node']['next_node'] = new_element
                self.tree_head[parent]['prev_node'] = new_element
            if new_node['id'] >= self.total_element:
                self.add_head_list_len(new_node['id'])
            if str(new_node['id']) not in self.nodes:
                self.nodes[str(new_node['id'])] = new_node
            else:
                print('duplicate id')
                sys.stderr.write('duplicate id')
                sys.exit(1)

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
        for _, node in self.nodes.items():
                record.Record_txt(record.record_file_name, str(node) + '\n', self.idx)
                print(node)
        record.Record_txt(record.record_file_name, '\n', self.idx)

    def child_to_list(self, id):
        child_list = []
        distance_list = []
        child_nodes_cost_time = []
        next = self.tree_head[id]['next_node']
        while next['node'] != None:
            child_list.append((next['node']['id'], next['node']['answer'], next['node']['value']))
            distance_list.append(next['node']['ancestor_distance'])
            child_nodes_cost_time.append(next['node']['generation cost time'] + next['node']['evaluation cost time'])
            next = next['next_node']
        return child_list, distance_list, child_nodes_cost_time
    
    def add_cost_time(self, ys, generation_cost_time_list:list = None, evaluation_cost_time_list:list = None):
        for i in range(len(ys)):
            print(ys[i][0])
            if generation_cost_time_list != None:
                self.nodes[str(ys[i][0])]['generation cost time'] = generation_cost_time_list[i]
            if evaluation_cost_time_list != None:
                self.nodes[str(ys[i][0])]['evaluation cost time'] = evaluation_cost_time_list[i]
                
    def __sort_nodes__(self):
        self.nodes = dict(sorted(self.nodes.items(), key=lambda item: int(item[0])))