from grid_diagram import HalfGridDiagram, GridDiagram
from queue import Queue
import math

class Tree:
    """ A class representing binary tree.

    Attributes:
        node_list (list): A list of nodes given by inorder traversal, each node is a string of '0' and '1's, representing the path to this node. '0' represents left edge, '1' represents right edge.
        leaf_list (list): A list of leaves from left to right.
        n_sign (list): A list of 0 and 1's. 0 represents - sign, 1 represents + sign.
        caret_pos (list): A list of carets' positions in the node_list. A node is called a caret if its left child and right child are both leaves.
        half_grid_diagram (HalfGridDiagram): The half grid diagram associated to the tree.
    """
    def __init__(self, node_list, iscomplete):
        """ Initializes a Tree object

        Args:
            node_list (list): A list of nodes.
            iscomplete (bool): If False, then only node_list will be initialized, and leaf_list, n_sign, caret_pos, half_grid_diagram will be not.
        """
        self.node_list = node_list

        if iscomplete == True:
            full_sign = [(l.count('1') + 1) % 2 for l in self.node_list]
            self.leaf_list = [self.node_list[i] for i in range(0, len(self.node_list), 2)]
            self.n_sign = [full_sign[i] for i in range(0, len(full_sign), 2)]

            depth_list = [len(n) for n in self.node_list]
            rel_depth_list = [None for n in self.node_list]
            count = 0
            for i in range(max(depth_list) + 1):
                for j in range(len(depth_list)):
                    if i == depth_list[j]:
                        rel_depth_list[j] = math.ceil(count)
                        count += 0.5

            self.caret_pos = []
            for i in range(1, len(depth_list) - 1, 2):
                if depth_list[i] == depth_list[i - 1] - 1 and depth_list[i] == depth_list[i + 1] - 1:
                    self.caret_pos.append(i)

            Xlist = [None for i in range(len(self.leaf_list))]
            Olist = [None for i in range(len(self.leaf_list))]
            for i in range(len(self.node_list)):
                if full_sign[i] == 1:
                    Xlist[rel_depth_list[i]] = i + 1
                else:
                    Olist[rel_depth_list[i]] = i + 1
            Olist[0] = 0
            self.half_grid_diagram = HalfGridDiagram(Xlist, Olist)
    
class TreeDiagram:
    """ A class representing tree diagram.
    
        Attributes:
            upper_tree (Tree): The upper tree.
            lower_tree (Tree): The lower tree.
    """

    def __init__(self, upper_tree, lower_tree):
        """ Initializes a TreeDiagram object.

        Args:
            upper_tree (Tree): The upper tree, must be initialized with iscomplete == True.
            lower_tree (Tree): The lower tree, must be initialized with iscomplete == True.
        """
        self.upper_tree = upper_tree
        self.lower_tree = lower_tree
    
    def isreduced(self):
        """ Returns whether the tree diagram is reduced."""
        return not any(c in self.upper_tree.caret_pos for c in self.lower_tree.caret_pos)
    
    def iscompatible(self):
        """ Returns whether the tree diagram is compatible."""
        return self.upper_tree.n_sign == self.lower_tree.n_sign
        
    def get_grid_diagram(self):
        """ Returns the grid diagram associated to the tree diagram. """
        return self.upper_tree.half_grid_diagram + self.lower_tree.half_grid_diagram