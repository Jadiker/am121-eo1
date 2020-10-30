import itertools
from typing import List

'''
A direction is a tuple
'''

def sum_directions(directions):
    return tuple([sum(zip_val) for zip_val in zip(*directions)])

def get_components(direction):
    '''Get the components of a direction'''
    ans = []
    for index, val in enumerate(direction):
        if val != 0:
            component = [0] * len(direction)
            component[index] = val
            ans.append(tuple(component))

    return ans

class Node:
    def __init__(self, name):
        self.name = name
        self.connections = set()

    def next_to(self, direction=None):
        '''Get the nodes and directions of the nodes this node is next to'''
        return [(node, node_direction) for node, node_direction in self.connections if node_direction == direction or direction is None]

    def connect_to(self, node, direction):
        # print("{} -> {} [direction: {}]".format(self.name, node.name, direction))
        self.connections.add((node, direction))

class Slot(Node):
    def __init__(self, name, value=None):
        super().__init__(name)
        self.value = value

    def set_value(self, new_value):
        self.value = new_value

    def get_value(self):
        return self.value


class Graph:
    '''
    restriction: direction and node must be hashable types
    '''
    def __init__(self, node_class=Node):
        self.graph = set()
        self.node_class = node_class

    def get_node(self, name):
        for node in self.graph:
            if node.name == name:
                return node
        raise RuntimeError("Name {} not found in graph".format(name))

    def add_node(self, name):
        self.graph.add(self.node_class(name))

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def connect_nodes(self, name1, name2, direction):
        node1 = self.get_node(name1)
        node2 = self.get_node(name2)
        node1.connect_to(node2, direction)
        node2.connect_to(node1, self.reverse_direction(direction))

    def get_next_to(self, name, direction=None):
        ans = self.get_node(name).next_to(direction=direction)
        # get the name instead of the node
        if ans:
            ans = [(node.name, node_dir) for node, node_dir in ans]
        return ans

    @classmethod
    def reverse_direction(self, direction):
        return tuple([-axis for axis in direction])

class Grid(Graph):
    def __init__(self, node_class=Node, dimensions: List[int]=None, diagonal=True):
        if dimensions is None:
            dimensions = []
        super().__init__(node_class=node_class)
        self.dimensions = dimensions
        coord_iter = [range(dim) for dim in dimensions]

        node_names = []
        # add all of the spots into the game
        for coord in itertools.product(*coord_iter):
            node_names.append(str(coord))
        self.add_nodes(node_names)

        unit_directions = [tuple([1 if index == dim_index else 0 for index in range(len(dimensions))]) for dim_index in range(len(dimensions))]

        # connect the nodes together in a grid-like fashion
        node_amt = len(node_names)
        nodes_per_hit = node_amt
        for dim_index, dim in enumerate(dimensions):
            direction = unit_directions[dim_index]
            nodes_per_hit //= dim
            hits_per_line = dim
            lines_per_pass = node_amt // (nodes_per_hit * hits_per_line)
            pass_amt = nodes_per_hit
            # we start off with a hit and then jump between each hit
            jumps_per_line = hits_per_line - 1
            # print("nodes_per_hit {}, hits_per_line: {}, lines_per_pass: {}, pass_amt: {}".format(nodes_per_hit, hits_per_line, lines_per_pass, pass_amt))
            for pass_index in range(pass_amt):
                current_index = pass_index
                for line_index in range(lines_per_pass):
                    for jump_index in range(jumps_per_line):
                        # print("current_index: {}".format(current_index))
                        self.connect_nodes(node_names[current_index], node_names[current_index + nodes_per_hit], direction)
                        current_index += nodes_per_hit
                    # print("finished line")
                    current_index += nodes_per_hit

        if diagonal:
            # connect the nodes diagonally in all directions
            all_possible_directions = list(itertools.product(*([(-1, 0, 1)] * len(dimensions))))
            unique_directions = []
            for possible_direction in all_possible_directions:
                if self.reverse_direction(possible_direction) not in unique_directions:
                    unique_directions.append(possible_direction)

            self.unique_directions = unique_directions

            for unique_direction in unique_directions:
                components = get_components(unique_direction)
                if len(components) < 2:
                    # skip over non-diagonals
                    continue

                for node_name in node_names:
                    cur_node_name = node_name
                    for component in components:
                        next_to = self.get_next_to(cur_node_name, component)
                        if next_to:
                            cur_node_name = next_to[0][0] # get the name of the node here
                        else:
                            cur_node_name = None
                            break
                    if cur_node_name:
                        self.connect_nodes(node_name, cur_node_name, unique_direction)
        else:
            # no diagonal connections
            self.unique_directions = unit_directions
