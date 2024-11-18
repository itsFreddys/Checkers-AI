from random import randint
from BoardClasses import Move
from BoardClasses import Board

import random
import math
import time

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

EXPLORATION_C = 2

class MCTNode():
    
    def __init__(self, color, move=None, parent=None):             
        self.wins = 0
        self.visit_count = 0
        self.children = []
        self.move = move 
        self.parent = parent
        self.color = color   
        
    def visit(self):
        self.visit_count += 1
       

def calculate_UCB(node: MCTNode):
    """calculate UCB value for a given node
        
       Formula:
       vi + C * sqrt(ln(N) / ni)
    """
    if node.visit_count == 0:
        return float('inf')
    else:
        return node.wins / node.visit_count + EXPLORATION_C * math.sqrt(math.log(node.parent.visit_count) / node.visit_count) 
    

def calculate_UCB1(node):
    if node.visit_count == 0:
        return float('inf')
    return node.wins / node.visit_count + (2 * (2 * node.parent.visit_count) ** 0.5 / node.visit_count) ** 0.5

     
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2    
        self.num_pieces = self.board.get_num_pieces(self.color)   

                
    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        start_time = time.time()
        root = MCTNode(self.opponent[self.color])
        # add all children nodes for root
        self.init_root_node(root)
        #sim_counter = 0
        # simulates for 5 seconds
        while time.time() - start_time < 8:
            selected_node = self.select(root)
            new_node = self.expand(selected_node)
            result = self.simulate(new_node)
            self.backpropagate(new_node, result)
            #sim_counter += 1

        # for _ in range(1000):
        #     selected_node = self.select(root)
        #     new_node = self.expand(selected_node)
        #     result = self.simulate(new_node)
        #     self.backpropagate(selected_node, result)

        # for child in root.children:
        #     print("child visits: ", child.visit_count, " wins: ", child.wins)

        # check if the best move for the best children will lose or win over some pieces, 
        # if piece results in the pieces being eaten, then we retract that move and try the second best child until we find a favorable outcome
        # double_check_moveset(root)

        best_child = self.get_best_child(root)
        # best_child = self.double_check_moveset(root)
        best_move = best_child.move
        self.board.make_move(best_move, self.color)

        return best_move
    
    def double_check_moveset(self, root: MCTNode):
        '''This will check if any of the movesets results in a bad move in which 
            the algor carelessy gets a piece eaten '''
        # value = -1
        # sorted_child_wins = max(sorted([child.wins for child in root.children], key=lambda x: x.wins))
        # max_value = max([child.wins for child in root.children])
        # lst = [child for child in root.children if child.wins == max_value]
        # best_child = random.choice(lst)
        og_pieces = self.board.get_num_pieces(self.color)
        op_pieces = self.board.get_num_pieces(self.opponent[root.color])
        op_color = self.opponent[root.color]

        sorted_children = sorted(root.children, key=lambda x: x.wins)

        for child in sorted_children:
            child_rate = 0
            self.board.make_move(child.move, child.color)
            next_color = self.opponent[root.color]
            rounds = 1
            counter = 0
            while counter < 3 or not self.is_gameover():
                # next play
                moves = self.board.get_all_possible_moves(next_color)
                index = randint(0, len(moves) - 1)
                inner_index = randint(0, len(moves[index]) - 1)            
                move = moves[index][inner_index]
                self.board.make_move(move, next_color)
                rounds += 1
                if self.board.get_num_pieces(self.color) < og_pieces:
                    # this means it lost a piece and this moveset may not be favorable
                    child_rate += -1
                elif self.board.get_num_pieces(op_color) < op_pieces:
                    child_rate += 1
                next_color = self.opponent[next_color]
                counter += 1
            # resetting the game
            # if player pieces is less than 4 then swictch ties = 1 and wins to .1, else wins = 1 and ties = .1
            for _ in range(rounds):
                self.board.undo()

            # check if current child actually is a good fit, double check if best_child is appropiate
            if child_rate >= 0:
                return child
        
        return sorted_children[0]
    
    def init_root_node(self, root):
        moves = self.board.get_all_possible_moves(self.color)
        for i in range(len(moves)):
            for j in range(len(moves[i])):             
                move = moves[i][j]
                new_node = MCTNode(self.color, move, root)
                root.children.append(new_node)

    
    def select(self, root):
        node = root
        next_color = self.opponent[node.color]
        while not len(node.children):
            node = self.find_child_by_ucb(node)
            self.board.make_move(node.move, next_color)
            next_color = self.opponent[node.color]         
                
        return node
    
    
    def expand(self, parent_node): 
        next_color = self.opponent[parent_node.color]
        moves = self.board.get_all_possible_moves(next_color)

        for i in range(len(moves)):
            for j in range(len(moves[i])):
                new_node = MCTNode(next_color, moves[i][j], parent_node)
                parent_node.children.append(new_node)            

        return random.choice(parent_node.children)    

        # index = randint(0, len(moves) - 1)
        # inner_index = randint(0, len(moves[index]) - 1)
        # move = moves[index][inner_index]
        # new_node = MCTNode(next_color, move, parent_node)
        # parent_node.children.append(new_node)
        # return new_node
    
    
    def simulate(self, node):
        self.board.make_move(node.move, node.color)
        next_color = self.opponent[node.color]
        rounds = 1
        while not self.is_gameover():
            # next play
            moves = self.board.get_all_possible_moves(next_color)
            index = randint(0, len(moves) - 1)
            inner_index = randint(0, len(moves[index]) - 1)            
            move = moves[index][inner_index]
            self.board.make_move(move, next_color)
            rounds += 1
            next_color = self.opponent[next_color]
        # resetting the game
        # if player pieces is less than 4 then swictch ties = 1 and wins to .1, else wins = 1 and ties = .1
        if self.num_pieces > 4:
            res = self.did_ai_win()
        else: 
            res = self.did_ai_tie()
        for _ in range(rounds):
            self.board.undo()
        return res
    

    def backpropagate(self, node, result):
        while node.parent:
            node.visit()
            if node.color == self.color:
                node.wins += result 
            node = node.parent

            
    def did_ai_win(self):
        result = self.board.is_win("")
        if result == self.color:
            return 1
        elif result == -1:
            return 0.2
        else:
            return 0  
        
    def did_ai_tie(self):
        result = self.board.is_win("")
        if result == self.color:
            return 0.2
        elif result == -1:
            return 1
        else:
            return 0
               
    
    def find_child_by_ucb(self, node):
        # best_ucb = 0
        best_child_node = node.children[0]

        max_ucb = max([calculate_UCB(child) for child in node.children])
        lst = [child for child in node.children if calculate_UCB(child) == max_ucb]
        best_child_node = random.choice(lst)

        # for child in node.children:
        #     temp_ucb = calculate_UCB(child)
        #     if temp_ucb > best_ucb:
        #         best_child_node = child
        #         best_ucb = temp_ucb
                
        return best_child_node
    
    
    def get_best_child(self, root):
        # value = -1
        max_value = max([child.wins for child in root.children])
        lst = [child for child in root.children if child.wins == max_value]
        best_child = random.choice(lst)

        # for child in root.children:
        #     if child.wins > value:
        #         best_child = child
                
        return best_child
        
    
    def evaluate(self):
        """evaluate the state of the game 
            
           Evaluation logic:
           takes the difference of number of pieces between us (StudentAI) and the opponent 
        """
        opponent_color = 2 if self.color == 1 else 1 
        return self.board.get_num_pieces(self.color) - self.board.get_num_pieces(opponent_color)
    
        
    def is_gameover(self):
        """returns true if there is a winner or a tie, otherwise returns false"""
        return True if self.board.is_win("") != 0 else False 
    

    def get_num_moves(self, color):
        moves = self.board.get_all_possible_moves(color)
        count = 0
        for lst in moves:
            count += len(lst)
        return count     
