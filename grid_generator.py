from tree_diagram import *
from grid_diagram import GridDiagram
from gridlink import XOlink
from progress.bar import Bar
from ctypes import *
import pickle
import platform
# import GridPythonModule as gp

def generate_tree_list(leaf_num, mode = 'continue'):
    """ Generate lists of all trees with leaf numbers smaller than or equal to leaf_num, store them in /data/tree_list_i.p.

    Args:
        leaf_num (int): The leaf number of the tree list returned.
        mode (str): Can be 'start' or 'continue'.

    Returns:
        (list): List of Tree objects with the given leaf number.
    """

    prev_tree_list = [[] for i in range(leaf_num -1)]
    if mode == 'start':
        prev_tree_list[0].append([''])
        for i in range(2, leaf_num):  # i is leaf number
            for j in range(1, i):  # j is leaf number of left tree
                for l in prev_tree_list[j - 1]:  # l is left tree
                    for r in prev_tree_list[i - j - 1]:  # r is right tree
                        l2 = ['0' + n for n in l]
                        r2 = ['1' + n for n in r]
                        prev_tree_list[i - 1].append(l2 + [''] + r2)
        for i in range(1, leaf_num):
            pickle.dump(prev_tree_list[i - 1], open("data/tree_list_" + str(i) + ".p", "wb"))
    elif mode == 'continue':
        for i in range(1, leaf_num):
            prev_tree_list[i - 1] = pickle.load(open("data/tree_list_" + str(i) + ".p", "rb")) 

    tree_list = []
    bar = Bar("Generating trees...", fill='$', max = leaf_num - 1, suffix = '%(percent)d%% --- %(elapsed)ds')
    for j in range(1, leaf_num):  # j is leaf number of left tree
        bar.next()
        for l in prev_tree_list[j - 1]:  # l is left tree
            for r in prev_tree_list[leaf_num - j - 1]: # r is right tree
                l2 = ['0' + n for n in l]
                r2 = ['1' + n for n in r]
                tree_list.append(l2 + [''] + r2)
    print()
    
    pickle.dump(tree_list, open("data/tree_list_" + str(leaf_num) + ".p", "wb"))
    # tree_list = pickle.load(open("code/data/tree_list_" + str(leaf_num) + ".p", "rb"))

    tree_list_ready = []
    bar = Bar("Generating half grid diagrams...", fill='$', max = len(tree_list), suffix = '%(index)d/%(max)d --- %(elapsed)ds')
    for i in range(len(tree_list)):
        bar.next()
        t = tree_list[i]
        tree_list_ready.append(Tree(t, True))
    print()
    return tree_list_ready

def generate_grid_diagram_list(leaf_num, tree_list):
    """ Generate list of grid diagrams constructed by reduced compatible tree diagrams in tree_list, up to vertical mirror.
    
    Args:
        leaf_num (int): The leaf number of tree_list.
        tree_list (list): A list of Tree objects with same leaf number leaf_num.

    Return:
        (list): List of GridDiagram objects.
    """

    tree_sorted_list = [[] for i in range(2 ** leaf_num)]  # can be list of pointer
    for t in tree_list:
        n_sign = t.n_sign
        n_sign_index = 0
        for i in range(leaf_num):
            n_sign_index += (2 ** i) * n_sign[i]
        tree_sorted_list[n_sign_index].append(t)

    grid_diagram_list = []
    bar = Bar("Generating grid diagrams...", fill='$', max = 2 ** leaf_num // 16, suffix = '%(percent)d%% --- %(elapsed)ds')
    for k in range(5, len(tree_sorted_list), 16):  # We assume that the first four signs must be +-+-
        # can be paralleled
        s = tree_sorted_list[k]
        length = len(s)
        bar.next()
        for i in range(length):
            u = s[i]  # upper tree
            for j in range(i + 1, length):
                l = s[j]  # lower tree
                td = TreeDiagram(u, l)
                if td.isreduced() == True:
                    grid_diagram_list.append(td.get_grid_diagram())
                else:
                    pass
    print()
    return grid_diagram_list

def find_nontrivial_knot(grid_diagram_list, min_grid_num=5):
    """ Find nontrival knots in a given list of grid diagrams.

    Args:
        grid_diagram_list (list): A list of GridDiagram objects.
    
    Returns:
        (list): A list of tuples. Each tuple contains a grid diagram of nontrivial knot, and its simplified grid diagram.
    
    """
    nontrivial_list = []
    length = len(grid_diagram_list)
    bar = Bar("Searching nontrival knots...", fill='$', max = length, suffix = '%(index)d/%(max)d --- %(elapsed)ds')
    for i in range(length):
        bar.next()
        gd = grid_diagram_list[i]
        
        # if gd.component_num() == 1:
        #     sgd = gd.simplify(effort='low')
        #     if sgd.grid_num >= min_grid_num:
        #         nontrivial_list.append((gd, sgd))

        L = XOlink(gd.Xlist, gd.Olist)
        if L.components == 1:
            L.simplify(1000, min_grid_num)
            if L.size >= min_grid_num:
                (Xlist, Olist) = L.get_XOlists()
                sgd = GridDiagram(Xlist, Olist)
                nontrivial_list.append((gd, sgd))
    print()
    return nontrivial_list

def find_URnonnull_knot(leaf_num, grid_diagram_list):
    URnonnull_list = []
    if platform.system() == 'Windows':
        transverse = CDLL('transverse_'+str(leaf_num)+'.dll')
    if platform.system() == 'Darwin':
        transverse = CDLL('transverse_'+str(leaf_num)+'.dylib')
    if platform.system() == 'Linux':
        transverse = CDLL('transverse_'+str(leaf_num)+'.so')
    bar = Bar("Searching UR non-null knots...", fill='$', max = len(grid_diagram_list), suffix = '%(index)d/%(max)d --- %(elapsed)ds')
    for grid in grid_diagram_list:
        bar.next()
        Xlist = [i+1 for i in grid.rotate_clockwise().flip().Xlist]
        Olist = [i+1 for i in grid.rotate_clockwise().flip().Olist]
        transverse.change_Xs((c_byte * (leaf_num*2))(*Xlist))
        transverse.change_Os((c_byte * (leaf_num*2))(*Olist))
        if transverse.is_URnull() == 0:
            print(Xlist)
            print(Olist)
            URnonnull_list.append(grid)
    print()
    return URnonnull_list

def find_LLnonnull_knot(leaf_num, grid_diagram_list):
    URnonnull_list = []
    if platform.system() == 'Windows':
        transverse = CDLL('transverse_'+str(leaf_num)+'.dll')
    if platform.system() == 'Darwin':
        transverse = CDLL('transverse_'+str(leaf_num)+'.dylib')
    if platform.system() == 'Linux':
        transverse = CDLL('transverse_'+str(leaf_num)+'.so')
    bar = Bar("Searching LL non-null knots...", fill='$', max = len(grid_diagram_list), suffix = '%(index)d/%(max)d --- %(elapsed)ds')
    for grid in grid_diagram_list:
        bar.next()
        Xlist = [i+1 for i in grid.rotate_clockwise().flip().Xlist]
        Olist = [i+1 for i in grid.rotate_clockwise().flip().Olist]
        transverse.change_Xs((c_byte * (leaf_num*2))(*Xlist))
        transverse.change_Os((c_byte * (leaf_num*2))(*Olist))
        if transverse.is_LLnull() == 0:
            print(Xlist)
            print(Olist)
            URnonnull_list.append(grid)
    print()
    return URnonnull_list
        
def find_equality_knot(leaf_num, grid_diagram_list, min_grid_num=5):
    """ Find out knots satisfying leaf_num = - max tb in a given list of grid diagrams.

    Args:
        leaf_num (int): The leaf number of grid diagrams (half of grid number) in grid_diagram_list.
        grid_diagram_list (list): A list of GridDiagram objects.
        lower_bound (int): The lower bound of minimal grid number of knots we want to consider.
    
    Returns:
        (list): A list of tuples. Each tuple contains a grid diagram of knot satisfying the equality, and its simplified grid diagram.
    """
    eq_list = []
    length = len(grid_diagram_list)
    for i in range(length):
        print("searching ---", 100 * i / length, "%", end = "\r")
        gd = grid_diagram_list[i]
        L = XOlink(gd.Xlist, gd.Olist)
        if L.components == 1:
            L.simplify(1000, min_grid_num)
            arc_num = L.size
            if arc_num >= min_grid_num:
                # gd.visualize()
                (Xlist, Olist) = L.get_XOlists()
                sgd = GridDiagram(Xlist, Olist)
                # sgd.visualize()
                tb = L.tb()
                L.reflect()
                tb2 = L.tb()
                # print("arc index: ", arc_num)
                # print("tb: ", (tb, tb2))
                # print()
                if -tb == leaf_num or -tb2 == leaf_num:
                    # (Xlist, Olist) = L.get_XOlists()
                    # sgd = GridDiagram(Xlist, Olist)
                    eq_list.append((gd, sgd))
                    gd.visualize()
                    sgd.visualize()
    
    return eq_list

def main():
    leaf_num = 13

    # tree_list_ready = generate_tree_list(leaf_num, mode = 'start')
    # pickle.dump(tree_list_ready, open("data/tree_list_ready_" + str(leaf_num) + ".p", "wb"))
    tree_list_ready = pickle.load(open("data/tree_list_ready_" + str(leaf_num) + ".p", "rb")) 

    # grid_diagram_list = generate_grid_diagram_list(leaf_num, tree_list_ready)
    # pickle.dump(grid_diagram_list, open("data/grid_diagram_list_" + str(leaf_num) + ".p", "wb"))
    # grid_diagram_list = pickle.load(open("data/grid_diagram_list_" + str(leaf_num) + ".p", "rb")) 
    
    # print("Number of grid diagrams: ", len(grid_diagram_list))

    # nontrivial_list = find_nontrivial_knot(grid_diagram_list, 8)
    # pickle.dump(nontrivial_list, open("data/nontrivial_knot_list_" + str(leaf_num) + ".p", "wb"))
    # nontrivial_list = pickle.load(open("data/nontrivial_knot_list_" + str(leaf_num) + ".p", "rb")) 

    # eq_list = find_equality_knot(leaf_num, grid_diagram_list, lower_bound = 7)
    
    # print("Number of nontrivial knots: ", len(nontrivial_list))
    # print("Number of eq knots: ", len(eq_list))

    # URnonnull_list = find_URnonnull_knot(leaf_num, [g[0] for g in nontrivial_list])
    # print("Number of URnonnull knots: ", len(URnonnull_list))

    # LLnonnull_list = find_LLnonnull_knot(leaf_num, [g[0] for g in nontrivial_list])
    # print("Number of LLnonnull knots: ", len(LLnonnull_list))

    transverse = CDLL('transverse_'+str(leaf_num)+'.dylib')

    tree_sorted_list = [[] for i in range(2 ** leaf_num)]  # can be list of pointer
    for t in tree_list_ready:
        n_sign = t.n_sign
        n_sign_index = 0
        for i in range(leaf_num):
            n_sign_index += (2 ** i) * n_sign[i]
        tree_sorted_list[n_sign_index].append(t)

    LLnonnull_list = []
    bar = Bar("Searching LL non null...", fill='$', max = 2 ** leaf_num // 16, suffix = '%(percent)d%% --- %(elapsed)ds')
    for k in range(5, len(tree_sorted_list), 16):  # We assume that the first four signs must be +-+-
        # can be paralleled
        s = tree_sorted_list[k]
        length = len(s)
        bar.next()
        for i in range(length):
            u = s[i]  # upper tree
            for j in range(i + 1, length):
                l = s[j]  # lower tree
                td = TreeDiagram(u, l)
                if td.isreduced() == True:
                    grid = td.get_grid_diagram()
                    if grid.is_nontrivial_knot(min_grid_num=8)==True:
                        Xlist = [i+1 for i in grid.rotate_clockwise().flip().Xlist]
                        Olist = [i+1 for i in grid.rotate_clockwise().flip().Olist]
                        transverse.change_Xs((c_byte * (leaf_num*2))(*Xlist))
                        transverse.change_Os((c_byte * (leaf_num*2))(*Olist))
                        if transverse.is_LLnull() == 0:
                            LLnonnull_list.append(grid)
                            pickle.dump(grid, open("data/LLnonnull_list_" + str(leaf_num) + ".p", "ab"))
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    print()
    print("Number of LLnonnull knots: ", len(LLnonnull_list))

if __name__ == '__main__':
    main()