import GridPythonModule as gp

class HalfGridDiagram:
    """ A class representing half grid diagram.

    Attributes:
        grid_num (int): The number of squares horizontally.
        Xlist (list): A list of positions of X markings. Xlist[i] is the position of the X marking on the ith row, counted from upper left.
        Olist (list): A list of positions of O markings. Olist[i] is the position of the O marking on the ith row, counted from upper left.
    """
    def __init__(self, Xlist, Olist):
        """ Initializes a HalfGridDiagram object.
        
        Args:
            Xlist (list): A list of positions of X markings.
            Olist (list): A list of positions of O markings.
        """
        self.grid_num = len(Xlist)
        self.Xlist = Xlist
        self.Olist = Olist

        # TODO: check whether it is a legal half grid diagram (Xlist and Olist cannot have intersection).

    def __add__(self, lower_diagram):
        """ Addition to another half grid diagram.

        Args:
            lower_diagram (HalfGridDiagram): The half grid diagram put below in addition operation.
        
        Returns:
            (GridDiagram): The resulting grid diagram obtained by addition.
        """
        lower_Xlist = [lower_diagram.Olist[self.grid_num - i - 1] for i in range(self.grid_num)]
        lower_Olist = [lower_diagram.Xlist[self.grid_num - i - 1] for i in range(self.grid_num)]

        return GridDiagram(self.Xlist + lower_Xlist, self.Olist + lower_Olist)
    
    def sym_rep(self):
        pass
    
    def XOmat(self):
        """ Returns a matrix with entries 'X' or 'O' or ' ', intuitively representing half grid diagram. """

        XOmat = [[' ' for j in range (self.grid_num * 2)] for i in range(self.grid_num)]

        for i in range(self.grid_num):
            XOmat[i][self.Xlist[i]] = 'X'
            XOmat[i][self.Olist[i]] = 'O'
        
        return XOmat
    
    def visualize(self):
        """ Visualizes half grid diagram in console. """

        XOmat = self.XOmat()
        print('+', end = '')
        print('-' * (self.grid_num * 4 + 1), end = '')
        print('+')
        for r in XOmat:
            print('|', end = ' ')
            for m in r:
                print(m, end = ' ')
            print('|')

class GridDiagram:
    """ A class representing grid diagram.

    Attributes:
        grid_num (int): The number of squares horizontally or vertically.
        Xlist (list): A list of positions of X markings. Xlist[i] is the position of the X marking on the ith row, counted from upper left.
        Olist (list): A list of positions of O markings. Olist[i] is the position of the O marking on the ith row, counted from upper left.
    """
    def __init__(self, Xlist, Olist):
        """ Initializes a GridDiagram object.
        
        Args:
            Xlist (list): A list of positions of X markings.
            Olist (list): A list of positions of O markings.
        """
        self.grid_num = len(Xlist)
        self.Xlist = Xlist
        self.Olist = Olist

    def XOmat(self):
        """ Returns a matrix with entries 'X' or 'O' or ' ', intuitively representing grid diagram. """

        XOmat = [[' ' for j in range (self.grid_num)] for i in range(self.grid_num)]
        
        for i in range(self.grid_num):
            XOmat[i][self.Xlist[i]] = 'X'
            XOmat[i][self.Olist[i]] = 'O'
        
        return XOmat
    
    def visualize(self):
        """ Visualizes grid diagram in console. """

        XOmat = self.XOmat()
        print('+', end = '')
        print('-' * (self.grid_num * 2 + 1), end = '')
        print('+')
        for r in XOmat:
            print('|', end = ' ')
            for m in r:
                print(m, end = ' ')
            print("|\n", end = '')
        print('+', end = '')
        print('-' * (self.grid_num * 2 + 1), end = '')
        print('+')

    def fancy_visualize(self):
        gp.draw_grid([self.Xlist, self.Olist])

    def component_num(self):
        return gp.number_of_components([self.Xlist, self.Olist])
    
    def simplify(self, effort='medium'):
        small_G = gp.simplify_grid([self.Xlist, self.Olist], effort)
        return GridDiagram(small_G[0], small_G[1])
    
    def flip(self):
        return GridDiagram(self.Olist, self.Xlist)
    
    def rotate_clockwise(self):
        Xlist = [None for _ in range(self.grid_num)]
        Olist = [None for _ in range(self.grid_num)]
        for i in range(self.grid_num):
            Xlist[self.Xlist[i]] = self.grid_num - i - 1
            Olist[self.Olist[i]] = self.grid_num - i - 1
        return GridDiagram(Xlist, Olist)