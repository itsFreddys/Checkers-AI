
class Node:
    def __init__(self, data, moveset):
        self.data = data
        self.moveset = moveset
        self.children = []
        self.score = 0
        self.uses = 0
class MCTS:
    def __init__(self):
        # dictionary containing all nodes
        self.nodes = {}

    def add_node(self, move, node_data):
        new_node = Node(node_data)
        self.nodes[move] = new_node
